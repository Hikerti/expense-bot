from aiogram import Router

from src.bot.handlers import add, commands, start


def setup_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(add.router)
    router.include_router(commands.router)  
    return router