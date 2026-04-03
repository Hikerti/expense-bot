import asyncio
import pytest
import pytest_asyncio
from sqlalchemy import text

from src.db.engine import engine, SessionFactory
from src.db.models import Base


@pytest.fixture(scope="session")
def event_loop():
    """Один event loop на все тесты."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Создаёт таблицы перед тестами, удаляет после."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed справочников для тестов
    from seed.references import main as seed_main
    await seed_main()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session():
    """Сессия с откатом после каждого теста."""
    async with SessionFactory() as session:
        yield session
        await session.rollback()