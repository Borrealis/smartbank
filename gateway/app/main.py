from fastapi import FastAPI

from app.api import router as api_router

app = FastAPI(title="SmartBank API GateWay")
app.include_router(api_router)


@app.get("/")
async def health_check():
    return {"status": "API Gateway is running"}
