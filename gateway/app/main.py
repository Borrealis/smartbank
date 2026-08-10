from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api import router as api_router
from app.database import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: sync_conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        )
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="SmartBank API GateWay", lifespan=lifespan)
app.include_router(api_router)


@app.get("/")
async def health_check():
    return {"status": "API Gateway is running"}
