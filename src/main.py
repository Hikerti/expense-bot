import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.middlewares import AdminMiddleware
from src.bot.router import setup_router
from src.config import settings
from src.services.scheduler import SchedulerService


async def main() -> None:
    session = AiohttpSession(timeout=30)
    bot = Bot(token=settings.bot_token, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(AdminMiddleware())

    dp.include_router(setup_router())

    scheduler = SchedulerService()
    scheduler.start()

    print("🚀 Бот и scheduler запущены")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())