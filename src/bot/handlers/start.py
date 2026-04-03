from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Отправь мне текст расхода, например:\n"
        "\"Заплатил 38 долларов за Tilda с карты Falcon\""
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Я умею принимать расход в свободной форме,\n"
        "задавать уточняющие вопросы и сохранять транзакцию."
    )