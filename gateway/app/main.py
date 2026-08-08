import uuid

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import local_session
from app.models import TaskRecord

app = FastAPI(title="SmartBank API GateWay")


@app.get("/")
async def health_check():
    return {"status": "API Gateway is running"}


class AskRequest(BaseModel):
    query: str


async def get_db():
    async with local_session() as session:
        yield session


@app.post("/ask")
async def ask_question(requests: AskRequest, db: AsyncSession = Depends(get_db)):
    task_id = str(uuid.uuid4())
    new_task = TaskRecord(task_id=task_id, query=requests.query, status="PENDING")
    db.add(new_task)
    await db.commit()
    return {"task_id": task_id, "status": "PENDING"}


@app.get("/status/{task_id}")
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    query = select(TaskRecord).where(TaskRecord.task_id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {"task_id": task.task_id, "status": task.status, "query": task.query}
