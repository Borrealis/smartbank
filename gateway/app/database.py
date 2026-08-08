from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DB_URL = "postgresql+asyncpg://admin:root@localhost:5432/smartbank"
engine = create_async_engine(DB_URL)
local_session = async_sessionmaker(engine)
