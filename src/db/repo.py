from __future__ import annotations

from typing import Sequence

from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.schemas import ExportFilter, TransactionCreate
from src.db.models import Account, Category, Commission, Tranche, Transaction


class ReferenceRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_categories(self) -> Sequence[Category]:
        result = await self.session.execute(
            select(Category)
            .where(Category.is_active.is_(True))
            .order_by(Category.name)
        )
        return result.scalars().all()

    async def get_accounts(self) -> Sequence[Account]:
        result = await self.session.execute(
            select(Account)
            .where(Account.is_active.is_(True))
            .order_by(Account.name)
        )
        return result.scalars().all()

    async def get_tranches(self) -> Sequence[Tranche]:
        result = await self.session.execute(
            select(Tranche)
            .where(Tranche.is_active.is_(True))
            .order_by(Tranche.name)
        )
        return result.scalars().all()

    async def get_category_by_code(self, code: str) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.code == code)
        )
        return result.scalar_one_or_none()

    async def get_account_by_code(self, code: str) -> Account | None:
        result = await self.session.execute(
            select(Account).where(Account.code == code)
        )
        return result.scalar_one_or_none()

    async def get_tranche_by_code(self, code: str) -> Tranche | None:
        result = await self.session.execute(
            select(Tranche).where(Tranche.code == code)
        )
        return result.scalar_one_or_none()


class TransactionRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: TransactionCreate) -> Transaction:
        transaction = Transaction(**data.model_dump())
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_by_id(self, transaction_id: int) -> Transaction | None:
        result = await self.session.execute(
            select(Transaction)
            .options(
                selectinload(Transaction.category),
                selectinload(Transaction.account),
                selectinload(Transaction.tranche),
                selectinload(Transaction.commissions),
                selectinload(Transaction.attachments),
            )
            .where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_last(self, limit: int = 5) -> Sequence[Transaction]:
        result = await self.session.execute(
            select(Transaction)
            .options(
                selectinload(Transaction.category),
                selectinload(Transaction.account),
                selectinload(Transaction.tranche),
            )
            .order_by(desc(Transaction.transaction_date), desc(Transaction.id))
            .limit(limit)
        )
        return result.scalars().all()

    async def delete(self, transaction_id: int) -> bool:
        transaction = await self.get_by_id(transaction_id)
        if not transaction:
            return False

        await self.session.delete(transaction)
        await self.session.commit()
        return True

    async def add_commission(
        self,
        transaction_id: int,
        amount,
        currency: str,
        fx_rate,
        amount_usd,
        description: str | None = None,
    ) -> Commission:
        commission = Commission(
            transaction_id=transaction_id,
            amount=amount,
            currency=currency,
            fx_rate=fx_rate,
            amount_usd=amount_usd,
            description=description,
        )
        self.session.add(commission)
        await self.session.commit()
        await self.session.refresh(commission)
        return commission

    async def list_for_export(self, filters: ExportFilter | None = None) -> Sequence[Transaction]:
        query = (
            select(Transaction)
            .options(
                selectinload(Transaction.category),
                selectinload(Transaction.account),
                selectinload(Transaction.tranche),
                selectinload(Transaction.commissions),
            )
            .order_by(Transaction.transaction_date.asc(), Transaction.id.asc())
        )

        if filters:
            if filters.date_from:
                query = query.where(Transaction.transaction_date >= filters.date_from)
            if filters.date_to:
                query = query.where(Transaction.transaction_date <= filters.date_to)
            if filters.status:
                query = query.where(Transaction.status == filters.status)
            if filters.tranche_id:
                query = query.where(Transaction.tranche_id == filters.tranche_id)

        result = await self.session.execute(query)
        return result.scalars().all()