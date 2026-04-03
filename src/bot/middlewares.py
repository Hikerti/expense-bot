from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from src.config import settings


class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        if isinstance(event, Message):
            user_id = event.from_user.id
            if user_id != settings.admin_user_id:
                await event.answer("⛔ У вас нет доступа к этому боту.")
                return
        return await handler(event, data)