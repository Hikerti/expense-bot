from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def category_keyboard() -> InlineKeyboardMarkup:
    categories = [
        ("ФОТ", "cat:fot"),
        ("ИТ сервисы", "cat:it_services"),
        ("Счета", "cat:bills"),
        ("HR", "cat:hr"),
        ("Вендоры", "cat:vendors"),
        ("Маркетинг", "cat:marketing"),
        ("Юридические", "cat:legal"),
        ("Офис", "cat:office"),
        ("Командировки", "cat:travel"),
    ]
    rows = [categories[i:i + 3] for i in range(0, len(categories), 3)]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=data) for name, data in row]
            for row in rows
        ]
    )


def account_keyboard() -> InlineKeyboardMarkup:
    accounts = [
        ("Falcon AED", "acc:falcon_aed"),
        ("Falcon карта", "acc:falcon_card"),
        ("ENB AED", "acc:enb_aed"),
        ("ENB USD", "acc:enb_usd"),
        ("Крипта", "acc:crypto"),
        ("Наличные", "acc:cash"),
    ]
    rows = [accounts[i:i + 2] for i in range(0, len(accounts), 2)]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=data) for name, data in row]
            for row in rows
        ]
    )


def tranche_keyboard() -> InlineKeyboardMarkup:
    tranches = [
        ("2025-Q1", "tr:2025_q1"),
        ("2025-Q2", "tr:2025_q2"),
        ("Личные CEO", "tr:personal_ceo"),
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=data)]
            for name, data in tranches
        ]
    )


def yes_no_keyboard(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да", callback_data=f"{prefix}:yes"),
                InlineKeyboardButton(text="Нет", callback_data=f"{prefix}:no"),
            ]
        ]
    )


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Сохранить", callback_data="confirm:save"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="confirm:cancel"),
            ]
        ]
    )