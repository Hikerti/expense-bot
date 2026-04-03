import pytest
from datetime import date
from decimal import Decimal

from src.core.enums import TransactionStatus
from src.core.schemas import ParsedExpense
from src.db.engine import SessionFactory
from src.db.repo import ReferenceRepo, TransactionRepo
from src.services.transaction import TransactionService


class TestTransactionService:

    @pytest.mark.asyncio
    async def test_prepare_create_data_usd(self):
        async with SessionFactory() as session:
            svc = TransactionService(
                transaction_repo=TransactionRepo(session),
                reference_repo=ReferenceRepo(session),
            )

            parsed = ParsedExpense(
                amount=Decimal("38.00"),
                currency="USD",
                description="Tilda subscription",
                category_code="it_services",
                account_code="falcon_card",
                tranche_code="2025_q1",
                date=date(2025, 3, 24),
                is_recurring=True,
                status=TransactionStatus.OK,
                confidence=0.95,
            )

            result = await svc.prepare_create_data(parsed=parsed)

            assert result.amount == Decimal("38.00")
            assert result.currency == "USD"
            assert result.fx_rate == Decimal("1.0000")
            assert result.amount_usd == Decimal("38.00")
            assert result.period == "2025-03"
            assert result.is_recurring is True

    @pytest.mark.asyncio
    async def test_prepare_create_data_aed(self):
        async with SessionFactory() as session:
            svc = TransactionService(
                transaction_repo=TransactionRepo(session),
                reference_repo=ReferenceRepo(session),
            )

            parsed = ParsedExpense(
                amount=Decimal("374.32"),
                currency="AED",
                description="LinkedIn subscription",
                category_code="it_services",
                account_code="falcon_card",
                tranche_code="2025_q1",
                date=date(2025, 3, 24),
                is_recurring=True,
                confidence=0.9,
            )

            result = await svc.prepare_create_data(
                parsed=parsed,
                fx_rate=Decimal("3.6500"),
            )

            assert result.currency == "AED"
            assert result.fx_rate == Decimal("3.6500")
            assert result.amount_usd == Decimal("102.55")

    @pytest.mark.asyncio
    async def test_missing_amount_raises(self):
        async with SessionFactory() as session:
            svc = TransactionService(
                transaction_repo=TransactionRepo(session),
                reference_repo=ReferenceRepo(session),
            )

            parsed = ParsedExpense(
                currency="USD",
                description="test",
                date=date.today(),
                is_recurring=False,
                category_code="it_services",
                account_code="falcon_card",
                tranche_code="2025_q1",
            )

            with pytest.raises(ValueError, match="Amount is required"):
                await svc.prepare_create_data(parsed=parsed)

    @pytest.mark.asyncio
    async def test_missing_category_raises(self):
        async with SessionFactory() as session:
            svc = TransactionService(
                transaction_repo=TransactionRepo(session),
                reference_repo=ReferenceRepo(session),
            )

            parsed = ParsedExpense(
                amount=Decimal("100"),
                currency="USD",
                description="test",
                date=date.today(),
                is_recurring=False,
                account_code="falcon_card",
                tranche_code="2025_q1",
            )

            with pytest.raises(ValueError, match="Category is required"):
                await svc.prepare_create_data(parsed=parsed)

    @pytest.mark.asyncio
    async def test_unknown_category_raises(self):
        async with SessionFactory() as session:
            svc = TransactionService(
                transaction_repo=TransactionRepo(session),
                reference_repo=ReferenceRepo(session),
            )

            parsed = ParsedExpense(
                amount=Decimal("100"),
                currency="USD",
                description="test",
                category_code="nonexistent_category",
                account_code="falcon_card",
                tranche_code="2025_q1",
                date=date.today(),
                is_recurring=False,
            )

            with pytest.raises(ValueError, match="Unknown category"):
                await svc.prepare_create_data(parsed=parsed)

    @pytest.mark.asyncio
    async def test_create_and_get_last(self):
        async with SessionFactory() as session:
            svc = TransactionService(
                transaction_repo=TransactionRepo(session),
                reference_repo=ReferenceRepo(session),
            )

            parsed = ParsedExpense(
                amount=Decimal("50.00"),
                currency="USD",
                description="Test transaction",
                category_code="office",
                account_code="cash",
                tranche_code="2025_q1",
                date=date.today(),
                is_recurring=False,
                confidence=0.8,
            )

            created = await svc.create_from_parsed(
                parsed=parsed,
                raw_input="тестовая транзакция",
            )

            assert created.id is not None

            last = await svc.get_last_transactions(limit=1)
            assert len(last) >= 1

    @pytest.mark.asyncio
    async def test_delete_transaction(self):
        async with SessionFactory() as session:
            svc = TransactionService(
                transaction_repo=TransactionRepo(session),
                reference_repo=ReferenceRepo(session),
            )

            parsed = ParsedExpense(
                amount=Decimal("10.00"),
                currency="USD",
                description="To be deleted",
                category_code="office",
                account_code="cash",
                tranche_code="2025_q1",
                date=date.today(),
                is_recurring=False,
            )

            created = await svc.create_from_parsed(parsed=parsed)
            assert await svc.delete_transaction(created.id) is True
            assert await svc.delete_transaction(999999) is False