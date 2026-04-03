from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.db.engine import SessionFactory
from src.db.repo import TransactionRepo


router = Router()


@router.message(Command("last"))
async def cmd_last(message: Message) -> None:
    async with SessionFactory() as session:
        repo = TransactionRepo(session)
        transactions = await repo.get_last(limit=5)

    if not transactions:
        await message.answer("Пока нет ни одной транзакции.")
        return

    lines = ["📋 Последние транзакции:\n"]
    for t in transactions:
        lines.append(
            f"• {t.transaction_date} | {t.amount} {t.currency} | {t.description}"
        )
        if t.category:
            lines.append(f"  Категория: {t.category.name}")
        if t.account:
            lines.append(f"  Счёт: {t.account.name}")
        lines.append("")

    await message.answer("\n".join(lines))