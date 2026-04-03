from sqlalchemy import func, select

from src.db.models import Transaction
from src.db.repo import TransactionRepo


class StatsService:
    def __init__(self, session):
        self.session = session

    async def get_summary(self):
        repo = TransactionRepo(self.session)
        transactions = await repo.list_for_export()

        total_usd = sum(t.amount_usd for t in transactions)
        recurring = sum(t.amount_usd for t in transactions if t.is_recurring)

        by_category = {}
        for t in transactions:
            cat = t.category.name if t.category else "Без категории"
            by_category[cat] = by_category.get(cat, 0) + float(t.amount_usd)

        return {
            "total_transactions": len(transactions),
            "total_usd": round(float(total_usd), 2),
            "recurring_usd": round(float(recurring), 2),
            "by_category": dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True))
        }