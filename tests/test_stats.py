import pytest
from decimal import Decimal
from datetime import date

from src.db.engine import SessionFactory
from src.db.repo import TransactionRepo, ReferenceRepo
from src.core.schemas import ParsedExpense
from src.services.stats import StatsService
from src.services.transaction import TransactionService


class TestStatsService:

    @pytest.mark.asyncio
    async def test_total_usd(self):
        async with SessionFactory() as session:
            stats = StatsService(session)
            total = await stats.total_usd()
            assert isinstance(total, Decimal)

    @pytest.mark.asyncio
    async def test_transaction_count(self):
        async with SessionFactory() as session:
            stats = StatsService(session)
            count = await stats.transaction_count()
            assert isinstance(count, int)
            assert count >= 0

    @pytest.mark.asyncio
    async def test_summary_by_category(self):
        async with SessionFactory() as session:
            stats = StatsService(session)
            result = await stats.summary_by_category()
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_summary_by_tranche(self):
        async with SessionFactory() as session:
            stats = StatsService(session)
            result = await stats.summary_by_tranche()
            assert isinstance(result, list)