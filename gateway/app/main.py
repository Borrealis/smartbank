from fastapi import FastAPI, HTTPException, status

from app.api import router as api_router
from app.broker import kafka_router

app = FastAPI(title="SmartBank API GateWay")
app.include_router(api_router)
app.include_router(kafka_router)


@app.get("/health")
async def health_check():
    kafka_live_status = await kafka_router.broker.ping(timeout=5)
    if not kafka_live_status:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Kafka unavailable"
        )
    return {"status": "healthy", "kafka": "available"}
