from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models import Base


@asynccontextmanager
async def lifespawn(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="SmartBank API GateWay", lifespawn=lifespawn)


@app.get("/")
async def health_check():
    return {"status": "API Gateway is running"}
