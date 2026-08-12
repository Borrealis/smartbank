from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="SmartBank API GateWay", lifespan=lifespan)
app.include_router(api_router)


@app.get("/")
async def health_check():
    return {"status": "API Gateway is running"}
