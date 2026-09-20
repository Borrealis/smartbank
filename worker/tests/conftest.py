import pytest_asyncio
from app.config import settings
from app.database import engine
from app.models import Base


@pytest_asyncio.fixture(scope="function", autouse=True)
async def auto_async_fixture():
    if settings.postgres_db != "smartbank_test":
        raise RuntimeError("Test must use smartbank_test database")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
