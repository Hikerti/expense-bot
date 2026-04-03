from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.db.engine import SessionFactory
from src.db.repo import TransactionRepo
from src.services.export import ExportService
from src.services.stats import StatsService


router = Router()


@router.message(Command("last"))
async def cmd_last(message: Message) -> None:
    async with SessionFactory() as session:
        repo = TransactionRepo(session)
        transactions = await repo.get_last(limit=5)

    if not transactions:
        await message.answer("Пока нет сохранённых транзакций.")
        return

    lines = ["📋 **Последние транзакции:**\n"]
    for t in transactions:
        category = t.category.name if t.category else "—"
        account = t.account.name if t.account else "—"
        lines.append(
            f"• {t.transaction_date.strftime('%d.%m.%Y')} | "
            f"{t.amount} {t.currency} | {t.description}\n"
            f"  Категория: {category} | Счёт: {account}"
        )

    await message.answer("\n".join(lines))


@router.message(Command("summary"))
async def cmd_summary(message: Message) -> None:
    await message.answer("Собираю сводку...")

    async with SessionFactory() as session:
        stats_service = StatsService(session)
        summary = await stats_service.get_summary()

    text = (
        f"📊 **Сводка расходов**\n\n"
        f"Всего транзакций: {summary['total_transactions']}\n"
        f"Общая сумма: {summary['total_usd']} USD\n"
        f"Повторяемые: {summary['recurring_usd']} USD\n\n"
        f"По категориям:\n"
    )

    for cat, amount in summary['by_category'].items():
        text += f"• {cat}: {amount} USD\n"

    await message.answer(text)


@router.message(Command("export"))
async def cmd_export(message: Message) -> None:
    await message.answer("Генерирую Excel-файл...")

    async with SessionFactory() as session:
        export_service = ExportService(session)
        file_path = await export_service.generate_excel()

    await message.answer_document(
        document=open(file_path, "rb"),
        caption="📊 Экспорт всех транзакций"
    )