from fastapi import FastAPI

from app.api import router as api_router
from app.broker import kafka_router

app = FastAPI(title="SmartBank API GateWay")
app.include_router(api_router)
app.include_router(kafka_router)


@app.get("/")
async def health_check():
    return {"status": "API Gateway is running"}
