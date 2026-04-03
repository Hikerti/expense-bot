from src.core.schemas import ParsedExpense, TransactionCreate


def format_parsed_expense(data: ParsedExpense) -> str:
    return (
        "Распознал вот что:\n"
        f"Сумма: {data.amount}\n"
        f"Валюта: {data.currency}\n"
        f"Описание: {data.description}\n"
        f"Категория: {data.category_code}\n"
        f"Счёт: {data.account_code}\n"
        f"Контрагент: {data.counterparty}\n"
        f"Дата: {data.date}\n"
        f"Повторяемый: {data.is_recurring}\n"
        f"Транш: {data.tranche_code}\n"
        f"Статус: {data.status}\n"
        f"Уверенность: {data.confidence}"
    )


def format_transaction_preview(data: TransactionCreate) -> str:
    return (
        "Проверь транзакцию перед сохранением:\n"
        f"Сумма: {data.amount} {data.currency}\n"
        f"Описание: {data.description}\n"
        f"Дата: {data.transaction_date}\n"
        f"Период: {data.period}\n"
        f"Контрагент: {data.counterparty}\n"
        f"Повторяемый: {'Да' if data.is_recurring else 'Нет'}\n"
        f"Статус: {data.status}\n"
        f"Курс: {data.fx_rate}\n"
        f"Сумма в USD: {data.amount_usd}\n"
        f"category_id: {data.category_id}\n"
        f"account_id: {data.account_id}\n"
        f"tranche_id: {data.tranche_id}"
    )