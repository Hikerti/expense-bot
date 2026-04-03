import asyncio
import os
from src.services.nlu import ExpenseNLUService

async def main():
    nlu = ExpenseNLUService()
    
    if not nlu.api_key:
        print("ОШИБКА: MISTRAL_API_KEY не найден в .env!")
        return

    text = "заплатил 38 долларов за tilda с карты falcon, это подписка"
    print(f"Отправляем запрос в Mistral...\nТекст: '{text}'\n")
    
    parsed = await nlu.parse_expense(text)
    
    print("Результат парсинга:")
    print("-" * 40)
    for key, val in parsed.model_dump().items():
        if val is not None:
            print(f"{key}: {val}")
    print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())