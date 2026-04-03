import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.router import setup_router
from src.config import settings


async def main() -> None:
    # Простая и стабильная конфигурация
    session = AiohttpSession(timeout=30)

    bot = Bot(token=settings.bot_token, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(setup_router())

    print("🚀 Бот запускается...")
    print("Пытаюсь подключиться к Telegram API...")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook удалён успешно.")
        print("Запускаю polling...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())