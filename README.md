# ExpenseBot — Telegram-бот для учёта расходов

Система учёта финансовых затрат для стартапа NovaTech Solutions.
CEO отправляет текстовое сообщение в Telegram — бот распознаёт данные через AI,
задаёт уточняющие вопросы и сохраняет транзакцию.

## Возможности

- **AI-парсинг** — отправь `"заплатил 38 долларов за Tilda с карты Falcon"`,
  бот сам определит сумму, валюту, категорию, счёт
- **Уточняющие вопросы** — если AI не уверен, бот спросит через inline-кнопки
- **Справочники** — категории, счета, транши хранятся в БД
- **Excel-экспорт** — `/export` генерирует `.xlsx` в формате листа CF
- **Статистика** — `/summary` показывает сводку по категориям и траншам
- **Бэкапы** — ежедневное автоматическое копирование БД
- **Напоминания** — бот пишет в 21:00: «Были транзакции сегодня?»

## Стек

| Компонент | Технология |
|-----------|-----------|
| Telegram SDK | aiogram 3.x |
| БД | SQLite + aiosqlite |
| ORM | SQLAlchemy 2.0 (async) |
| Миграции | Alembic |
| NLU | Mistral AI API |
| Excel | openpyxl |
| Планировщик | APScheduler |
| Деплой | Docker Compose |

## Быстрый старт

### 1. Клонировать и настроить

```bash
git clone <repo>
cd expense-bot
cp .env.example .env
# Заполнить .env реальными данными

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -e ".[dev]"

3. Создать БД и заполнить справочники

python -m alembic upgrade head
python -m seed.references

python -m src.main

docker compose up -d --build

# Тесты
python -m pytest tests/ -v