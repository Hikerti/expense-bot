from __future__ import annotations

import json
import re
from datetime import date
from decimal import Decimal
from typing import Any

import aiohttp

from src.config import settings
from src.core.enums import TransactionStatus
from src.core.schemas import ParsedExpense


class ExpenseNLUService:
    def __init__(self) -> None:
        self.api_key = settings.mistral_api_key
        self.api_url = "https://api.mistral.ai/v1/chat/completions"

    async def parse_expense(self, text: str) -> ParsedExpense:
        if not self.api_key:
            print("ВНИМАНИЕ: MISTRAL_API_KEY не задан. Использую fallback.")
            return self._fallback_parse(text)

        try:
            response_text = await self._ask_mistral(text)
            
            data = self._extract_json(response_text)
            
            normalized = self._normalize_payload(data)
            
            if not normalized.get("description"):
                normalized["description"] = text.strip()

            return ParsedExpense(**normalized)

        except Exception as e:
            print(f"Ошибка LLM парсинга: {e}. Использую fallback.")
            return self._fallback_parse(text)

    async def _ask_mistral(self, text: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        prompt = self._build_prompt(text)
        
        payload = {
            "model": "mistral-small-latest",
            "temperature": 0.0,
            "response_format": {"type": "json_object"}, 
            "messages": [
                {
                    "role": "system",
                    "content": "Ты финансовый ассистент. Твоя задача — извлекать структурированные данные из текста и возвращать строго валидный JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise ValueError(f"Mistral API Error {resp.status}: {error_text}")
                
                result = await resp.json()
                return result["choices"][0]["message"]["content"]

    @staticmethod
    def _build_prompt(text: str) -> str:
        current_date = date.today().isoformat()
        return f"""
Текущая дата: {current_date}.
Извлеки из текста пользователя поля финансовой транзакции.

Доступные category_code: fot, it_services, bills, hr, vendors, marketing, legal, office, travel
Доступные account_code: falcon_aed, falcon_card, enb_aed, enb_usd, crypto, cash
Доступные tranche_code: 2025_q1, 2025_q2, personal_ceo
Доступные status: ok, creditor, forecast

Верни строго JSON объект такого формата:
{{
  "amount": число или null,
  "currency": "AED" или "USD" или null,
  "description": краткая суть расхода или null,
  "category_code": один из списка или null,
  "account_code": один из списка или null,
  "counterparty": кому заплатили (строка) или null,
  "date": "YYYY-MM-DD" или null (используй текущую дату если сегодня/вчера, иначе null),
  "is_recurring": true/false или null,
  "tranche_code": один из списка или null,
  "status": один из списка или null,
  "confidence": число от 0.0 до 1.0 (насколько ты уверен)
}}

Если поле нельзя определить точно — верни null. Не придумывай.

Текст пользователя:
"{text}"
"""

    @staticmethod
    def _extract_json(response_text: str) -> dict[str, Any]:
        response_text = response_text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in LLM response")
            return json.loads(match.group(0))

    @staticmethod
    def _normalize_payload(data: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(data)

        if normalized.get("amount") is not None:
            normalized["amount"] = Decimal(str(normalized["amount"]))

        if normalized.get("currency"):
            normalized["currency"] = str(normalized["currency"]).upper()

        if normalized.get("date"):
            try:
                normalized["date"] = date.fromisoformat(normalized["date"])
            except ValueError:
                normalized["date"] = None

        if normalized.get("status"):
            try:
                normalized["status"] = TransactionStatus(str(normalized["status"]).lower())
            except ValueError:
                normalized["status"] = None
        else:
            normalized["status"] = TransactionStatus.OK

        confidence = normalized.get("confidence", 0.0)
        normalized["confidence"] = float(confidence)

        return normalized

    @staticmethod
    def _fallback_parse(text: str) -> ParsedExpense:
        lowered = text.lower()
        amount_match = re.search(r"(\d+[.,]?\d*)", lowered)
        amount = Decimal(amount_match.group(1).replace(",", ".")) if amount_match else None
        
        currency = "USD" if "usd" in lowered or "доллар" in lowered else "AED" if "aed" in lowered or "дирхам" in lowered else None
        
        return ParsedExpense(
            amount=amount,
            currency=currency,
            description=text.strip(),
            date=None,  
            status=TransactionStatus.OK,
            confidence=0.1
        )