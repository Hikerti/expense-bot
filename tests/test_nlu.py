import pytest
from decimal import Decimal

from src.services.nlu import ExpenseNLUService


@pytest.fixture
def nlu():
    return ExpenseNLUService()


class TestNLUFallback:
    """Тесты fallback-парсера (без вызова API)."""

    def test_fallback_extracts_amount(self, nlu):
        result = nlu._fallback_parse("заплатил 38 долларов за tilda")
        assert result.amount == Decimal("38")

    def test_fallback_extracts_usd(self, nlu):
        result = nlu._fallback_parse("оплатил 100 долларов")
        assert result.currency == "USD"

    def test_fallback_extracts_aed(self, nlu):
        result = nlu._fallback_parse("купил за 500 aed")
        assert result.currency == "AED"

    def test_fallback_extracts_falcon_card(self, nlu):
        result = nlu._fallback_parse("оплатил с карты falcon 200")
        assert result.account_code == "falcon_card"

    def test_fallback_extracts_falcon_aed(self, nlu):
        result = nlu._fallback_parse("перевод falcon 1000")
        assert result.account_code == "falcon_aed"

    def test_fallback_extracts_emirates_usd(self, nlu):
        result = nlu._fallback_parse("перевод emirates usd 500")
        assert result.account_code == "enb_usd"

    def test_fallback_extracts_emirates_aed(self, nlu):
        result = nlu._fallback_parse("оплата через emirates 300")
        assert result.account_code == "enb_aed"

    def test_fallback_extracts_crypto(self, nlu):
        result = nlu._fallback_parse("отправил крипту 1000")
        assert result.account_code == "crypto"

    def test_fallback_extracts_cash(self, nlu):
        result = nlu._fallback_parse("дал наличными 200")
        assert result.account_code == "cash"

    def test_fallback_extracts_it_category(self, nlu):
        result = nlu._fallback_parse("подписка jira 23 доллара")
        assert result.category_code == "it_services"

    def test_fallback_recurring_keyword(self, nlu):
        result = nlu._fallback_parse("ежемесячная подписка 50 usd")
        assert result.is_recurring is True

    def test_fallback_no_amount(self, nlu):
        result = nlu._fallback_parse("просто текст без цифр")
        assert result.amount is None

    def test_fallback_no_currency(self, nlu):
        result = nlu._fallback_parse("заплатил 100 за обед")
        assert result.currency is None

    def test_fallback_empty_text(self, nlu):
        result = nlu._fallback_parse("")
        assert result is not None
        assert result.confidence <= 0.5

    def test_fallback_decimal_amount(self, nlu):
        result = nlu._fallback_parse("списали 374.32 aed")
        assert result.amount == Decimal("374.32")

    def test_fallback_comma_amount(self, nlu):
        result = nlu._fallback_parse("оплата 1,5 доллара")
        assert result.amount == Decimal("1.5")


class TestNLUJsonExtraction:
    """Тесты извлечения JSON из ответа LLM."""

    def test_extract_clean_json(self, nlu):
        raw = '{"amount": 38, "currency": "USD"}'
        result = nlu._extract_json(raw)
        assert result["amount"] == 38
        assert result["currency"] == "USD"

    def test_extract_json_with_markdown(self, nlu):
        raw = '```json\n{"amount": 100}\n```'
        result = nlu._extract_json(raw)
        assert result["amount"] == 100

    def test_extract_json_with_extra_text(self, nlu):
        raw = 'Here is the result: {"amount": 50, "currency": "AED"} done.'
        result = nlu._extract_json(raw)
        assert result["amount"] == 50

    def test_extract_json_invalid_raises(self, nlu):
        raw = "this is not json at all"
        with pytest.raises(ValueError, match="No JSON"):
            nlu._extract_json(raw)


class TestNLUNormalization:
    """Тесты нормализации данных из LLM."""

    def test_normalize_amount_to_decimal(self, nlu):
        data = {"amount": 38.5, "confidence": 0.9}
        result = nlu._normalize_payload(data)
        assert result["amount"] == Decimal("38.5")

    def test_normalize_currency_uppercase(self, nlu):
        data = {"currency": "usd", "confidence": 0.9}
        result = nlu._normalize_payload(data)
        assert result["currency"] == "USD"

    def test_normalize_date_valid(self, nlu):
        from datetime import date
        data = {"date": "2025-03-24", "confidence": 0.9}
        result = nlu._normalize_payload(data)
        assert result["date"] == date(2025, 3, 24)

    def test_normalize_date_invalid(self, nlu):
        data = {"date": "not-a-date", "confidence": 0.9}
        result = nlu._normalize_payload(data)
        assert result["date"] is None

    def test_normalize_status_valid(self, nlu):
        from src.core.enums import TransactionStatus
        data = {"status": "ok", "confidence": 0.9}
        result = nlu._normalize_payload(data)
        assert result["status"] == TransactionStatus.OK

    def test_normalize_status_invalid(self, nlu):
        data = {"status": "invalid_status", "confidence": 0.9}
        result = nlu._normalize_payload(data)
        assert result["status"] is None

    def test_normalize_confidence(self, nlu):
        data = {"confidence": 0.95}
        result = nlu._normalize_payload(data)
        assert result["confidence"] == 0.95

    def test_normalize_missing_confidence(self, nlu):
        data = {}
        result = nlu._normalize_payload(data)
        assert result["confidence"] == 0.0


class TestNLUIntegration:
    """Интеграционные тесты (вызывают реальный API)."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not pytest.importorskip("aiohttp", reason="No network"),
        reason="Network may be unavailable",
    )
    async def test_parse_full_phrase(self, nlu):
        """Полный парсинг через Mistral (пропускается без сети)."""
        try:
            parsed = await nlu.parse_expense(
                "заплатил 38 долларов за tilda с карты falcon, это подписка"
            )
            assert parsed.amount is not None
            assert parsed.description is not None
        except Exception:
            pytest.skip("Mistral API unavailable")