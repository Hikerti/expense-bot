from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.formatters import format_transaction_preview
from src.bot.keyboards import (
    account_keyboard,
    category_keyboard,
    confirm_keyboard,
    tranche_keyboard,
    yes_no_keyboard,
)
from src.bot.states import AddExpense
from src.core.schemas import ParsedExpense
from src.db.engine import SessionFactory
from src.db.repo import ReferenceRepo, TransactionRepo
from src.services.nlu import ExpenseNLUService
from src.services.transaction import TransactionService


router = Router()


@router.message(F.text)
async def handle_expense_text(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    nlu_service = ExpenseNLUService()
    parsed = await nlu_service.parse_expense(text)

    await state.update_data(raw_input=text, parsed=parsed.model_dump(mode="json"))

    if parsed.category_code is None:
        await state.set_state(AddExpense.ask_category)
        await message.answer("Выбери категорию:", reply_markup=category_keyboard())
        return

    if parsed.account_code is None:
        await state.set_state(AddExpense.ask_account)
        await message.answer("Выбери счёт:", reply_markup=account_keyboard())
        return

    if parsed.tranche_code is None:
        await state.set_state(AddExpense.ask_tranche)
        await message.answer("Выбери транш:", reply_markup=tranche_keyboard())
        return

    if parsed.is_recurring is None:
        await state.set_state(AddExpense.ask_recurring)
        await message.answer("Это повторяемый расход?", reply_markup=yes_no_keyboard("rec"))
        return

    await _show_confirmation(message, state)


@router.callback_query(AddExpense.ask_category, F.data.startswith("cat:"))
async def handle_category(callback: CallbackQuery, state: FSMContext) -> None:
    category_code = callback.data.split(":", 1)[1]
    data = await state.get_data()
    parsed = ParsedExpense(**data["parsed"])
    parsed.category_code = category_code

    await state.update_data(parsed=parsed.model_dump(mode="json"))

    if parsed.account_code is None:
        await state.set_state(AddExpense.ask_account)
        await callback.message.answer("Выбери счёт:", reply_markup=account_keyboard())
    elif parsed.tranche_code is None:
        await state.set_state(AddExpense.ask_tranche)
        await callback.message.answer("Выбери транш:", reply_markup=tranche_keyboard())
    elif parsed.is_recurring is None:
        await state.set_state(AddExpense.ask_recurring)
        await callback.message.answer(
            "Это повторяемый расход?",
            reply_markup=yes_no_keyboard("rec"),
        )
    else:
        await _show_confirmation(callback.message, state)

    await callback.answer()


@router.callback_query(AddExpense.ask_account, F.data.startswith("acc:"))
async def handle_account(callback: CallbackQuery, state: FSMContext) -> None:
    account_code = callback.data.split(":", 1)[1]
    data = await state.get_data()
    parsed = ParsedExpense(**data["parsed"])
    parsed.account_code = account_code

    await state.update_data(parsed=parsed.model_dump(mode="json"))

    if parsed.tranche_code is None:
        await state.set_state(AddExpense.ask_tranche)
        await callback.message.answer("Выбери транш:", reply_markup=tranche_keyboard())
    elif parsed.is_recurring is None:
        await state.set_state(AddExpense.ask_recurring)
        await callback.message.answer(
            "Это повторяемый расход?",
            reply_markup=yes_no_keyboard("rec"),
        )
    else:
        await _show_confirmation(callback.message, state)

    await callback.answer()


@router.callback_query(AddExpense.ask_tranche, F.data.startswith("tr:"))
async def handle_tranche(callback: CallbackQuery, state: FSMContext) -> None:
    tranche_code = callback.data.split(":", 1)[1]
    data = await state.get_data()
    parsed = ParsedExpense(**data["parsed"])
    parsed.tranche_code = tranche_code

    await state.update_data(parsed=parsed.model_dump(mode="json"))

    if parsed.is_recurring is None:
        await state.set_state(AddExpense.ask_recurring)
        await callback.message.answer(
            "Это повторяемый расход?",
            reply_markup=yes_no_keyboard("rec"),
        )
    else:
        await _show_confirmation(callback.message, state)

    await callback.answer()


@router.callback_query(AddExpense.ask_recurring, F.data.startswith("rec:"))
async def handle_recurring(callback: CallbackQuery, state: FSMContext) -> None:
    recurring_value = callback.data.split(":", 1)[1]
    data = await state.get_data()
    parsed = ParsedExpense(**data["parsed"])
    parsed.is_recurring = recurring_value == "yes"

    await state.update_data(parsed=parsed.model_dump(mode="json"))
    await _show_confirmation(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "confirm:save")
async def handle_confirm_save(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    parsed = ParsedExpense(**data["parsed"])
    raw_input = data.get("raw_input")

    async with SessionFactory() as session:
        transaction_service = TransactionService(
            transaction_repo=TransactionRepo(session),
            reference_repo=ReferenceRepo(session),
        )
        transaction = await transaction_service.create_from_parsed(
            parsed=parsed,
            raw_input=raw_input,
            fx_rate=Decimal("3.6500") if parsed.currency == "AED" else None,
        )

    await state.clear()
    await callback.message.answer(f"Транзакция сохранена ✅ ID: {transaction.id}")
    await callback.answer()


@router.callback_query(F.data == "confirm:cancel")
async def handle_confirm_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Операция отменена.")
    await callback.answer()


async def _show_confirmation(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    parsed = ParsedExpense(**data["parsed"])
    raw_input = data.get("raw_input")

    async with SessionFactory() as session:
        transaction_service = TransactionService(
            transaction_repo=TransactionRepo(session),
            reference_repo=ReferenceRepo(session),
        )
        create_data = await transaction_service.prepare_create_data(
            parsed=parsed,
            raw_input=raw_input,
            fx_rate=Decimal("3.6500") if parsed.currency == "AED" else None,
        )

    await state.set_state(AddExpense.confirm)
    await message.answer(
        format_transaction_preview(create_data),
        reply_markup=confirm_keyboard(),
    )