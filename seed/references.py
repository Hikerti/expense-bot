import asyncio

from sqlalchemy import select

from src.db.engine import SessionFactory
from src.db.models import Account, Category, Tranche


CATEGORIES = [
    {"name": "ФОТ", "code": "fot"},
    {"name": "ИТ сервисы", "code": "it_services"},
    {"name": "Счета", "code": "bills"},
    {"name": "HR", "code": "hr"},
    {"name": "Вендоры", "code": "vendors"},
    {"name": "Маркетинг", "code": "marketing"},
    {"name": "Юридические", "code": "legal"},
    {"name": "Офис", "code": "office"},
    {"name": "Командировки", "code": "travel"},
]

ACCOUNTS = [
    {"name": "Falcon AED", "code": "falcon_aed", "currency": "AED"},
    {"name": "Falcon карта AED", "code": "falcon_card", "currency": "AED"},
    {"name": "Emirates NB AED", "code": "enb_aed", "currency": "AED"},
    {"name": "Emirates NB USD", "code": "enb_usd", "currency": "USD"},
    {"name": "Крипта", "code": "crypto", "currency": "USD"},
    {"name": "Наличные", "code": "cash", "currency": None},
]

TRANCHES = [
    {"name": "2025-Q1", "code": "2025_q1"},
    {"name": "2025-Q2", "code": "2025_q2"},
    {"name": "Личные CEO", "code": "personal_ceo"},
]


async def seed_categories() -> None:
    async with SessionFactory() as session:
        for item in CATEGORIES:
            exists = await session.scalar(
                select(Category).where(Category.code == item["code"])
            )
            if not exists:
                session.add(Category(**item))
        await session.commit()


async def seed_accounts() -> None:
    async with SessionFactory() as session:
        for item in ACCOUNTS:
            exists = await session.scalar(
                select(Account).where(Account.code == item["code"])
            )
            if not exists:
                session.add(Account(**item))
        await session.commit()


async def seed_tranches() -> None:
    async with SessionFactory() as session:
        for item in TRANCHES:
            exists = await session.scalar(
                select(Tranche).where(Tranche.code == item["code"])
            )
            if not exists:
                session.add(Tranche(**item))
        await session.commit()


async def main() -> None:
    await seed_categories()
    await seed_accounts()
    await seed_tranches()
    print("Reference data seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())