import asyncio
import shutil
from datetime import date
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import settings


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.timezone)

    def start(self):
        self.scheduler.add_job(
            self.daily_backup,
            'cron',
            hour=23,
            minute=0
        )

        self.scheduler.add_job(
            self.send_reminder,
            'cron',
            hour=21,
            minute=0
        )

        self.scheduler.start()
        print("✅ Scheduler запущен")

    async def daily_backup(self):
        src = Path("data/expense.db")
        if not src.exists():
            return

        backup_dir = Path("data/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_name = f"expense_{date.today().isoformat()}.db"
        dst = backup_dir / backup_name

        shutil.copy2(src, dst)
        print(f"✅ Бэкап создан: {backup_name}")

        for old in sorted(backup_dir.glob("*.db"))[:-30]:
            old.unlink()

    async def send_reminder(self):

        print("🔔 Напоминание: не забудьте внести расходы за сегодня!")