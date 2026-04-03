from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from src.core.enums import TransactionStatus
from src.core.schemas import ParsedExpense, TransactionCreate
from src.db.repo import ReferenceRepo, TransactionRepo


class TransactionService:
    def __init__(
        self,
        transaction_repo: TransactionRepo,
        reference_repo: ReferenceRepo,
    ) -> None:
        self.transaction_repo = transaction_repo
        self.reference_repo = reference_repo

    async def prepare_create_data(
        self,
        parsed: ParsedExpense,
        raw_input: str | None = None,
        fx_rate: Decimal | None = None,
    ) -> TransactionCreate:
        if parsed.amount is None:
            raise ValueError("Amount is required")

        if not parsed.currency:
            raise ValueError("Currency is required")

        if not parsed.description:
            raise ValueError("Description is required")

        if parsed.date is None:
            raise ValueError("Transaction date is required")

        if parsed.is_recurring is None:
            raise ValueError("Recurring flag is required")

        if not parsed.category_code:
            raise ValueError("Category is required")

        if not parsed.account_code:
            raise ValueError("Account is required")

        if not parsed.tranche_code:
            raise ValueError("Tranche is required")

        category = await self.reference_repo.get_category_by_code(parsed.category_code)
        if category is None:
            raise ValueError(f"Unknown category code: {parsed.category_code}")

        account = await self.reference_repo.get_account_by_code(parsed.account_code)
        if account is None:
            raise ValueError(f"Unknown account code: {parsed.account_code}")

        tranche = await self.reference_repo.get_tranche_by_code(parsed.tranche_code)
        if tranche is None:
            raise ValueError(f"Unknown tranche code: {parsed.tranche_code}")

        normalized_currency = parsed.currency.upper()

        resolved_fx_rate = self._resolve_fx_rate(
            currency=normalized_currency,
            provided_rate=fx_rate,
        )
        amount_usd = self._calculate_amount_usd(parsed.amount, resolved_fx_rate)
        period = self._make_period(parsed.date)

        return TransactionCreate(
            amount=parsed.amount,
            currency=normalized_currency,
            description=parsed.description,
            transaction_date=parsed.date,
            period=period,
            counterparty=parsed.counterparty,
            is_recurring=parsed.is_recurring,
            status=parsed.status or TransactionStatus.OK,
            comment=parsed.comment,
            fx_rate=resolved_fx_rate,
            amount_usd=amount_usd,
            category_id=category.id,
            account_id=account.id,
            tranche_id=tranche.id,
            raw_input=raw_input,
            parse_confidence=Decimal(str(parsed.confidence)).quantize(Decimal("0.01")),
        )

    async def create_from_parsed(
        self,
        parsed: ParsedExpense,
        raw_input: str | None = None,
        fx_rate: Decimal | None = None,
    ):
        create_data = await self.prepare_create_data(
            parsed=parsed,
            raw_input=raw_input,
            fx_rate=fx_rate,
        )
        return await self.transaction_repo.create(create_data)

    async def get_last_transactions(self, limit: int = 5):
        return await self.transaction_repo.get_last(limit=limit)

    async def delete_transaction(self, transaction_id: int) -> bool:
        return await self.transaction_repo.delete(transaction_id)

    @staticmethod
    def _make_period(value: date) -> str:
        return value.strftime("%Y-%m")

    @staticmethod
    def _resolve_fx_rate(currency: str, provided_rate: Decimal | None) -> Decimal:
        if currency == "USD":
            return Decimal("1.0000")

        if currency == "AED":
            return provided_rate or Decimal("3.6500")

        if provided_rate is not None:
            return provided_rate

        raise ValueError(f"FX rate is required for currency: {currency}")

    @staticmethod
    def _calculate_amount_usd(amount: Decimal, fx_rate: Decimal) -> Decimal:
        return (amount / fx_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)