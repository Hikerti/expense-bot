from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import select

from src.db.models import Transaction
from src.db.repo import TransactionRepo


class ExportService:
    def __init__(self, session):
        self.session = session

    async def generate_excel(self) -> str:
        repo = TransactionRepo(self.session)
        transactions = await repo.list_for_export()

        wb = Workbook()
        ws = wb.active
        ws.title = "CF"

        # Заголовки
        headers = [
            "Категория", "Период", "Дата", "Контрагент", "С какого счёта",
            "Суть операции", "Валюта", "Сумма", "Курс перевода",
            "Сумма в USD", "Повторяемые", "Статус", "Транш"
        ]
        ws.append(headers)

        # Данные
        for t in transactions:
            row = [
                t.category.name if t.category else "",
                t.period,
                t.transaction_date.strftime("%d.%m.%Y"),
                t.counterparty or "",
                t.account.name if t.account else "",
                t.description,
                t.currency,
                float(t.amount),
                float(t.fx_rate),
                float(t.amount_usd),
                "Да" if t.is_recurring else "Нет",
                t.status.value.upper(),
                t.tranche.name if t.tranche else "",
            ]
            ws.append(row)

        # Форматирование
        for cell in ws[1]:
            cell.font = Font(bold=True)

        # Сохраняем
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        file_path = Path("data") / filename
        wb.save(file_path)

        return str(file_path)