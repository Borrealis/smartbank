from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = "postgresql+asyncpg://admin:root@db:5432/smartbank"
engine = create_async_engine(DATABASE_URL)
local_session = async_sessionmaker(engine)
