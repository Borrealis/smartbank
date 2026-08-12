import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import local_session
from app.models import TaskRecord

router = APIRouter()


class AskRequest(BaseModel):
    query: str


class TaskResponse(BaseModel):
    query: str
    status: str


async def get_db():
    async with local_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@router.post("/ask", response_model=TaskResponse)
async def ask_question(requests: AskRequest, db: AsyncSession = Depends(get_db)):
    task_id = str(uuid.uuid4())
    new_task = TaskRecord(task_id=task_id, query=requests.query, status="PENDING")
    db.add(new_task)
    return {"task_id": task_id, "status": "PENDING"}


@router.get("/status/{task_id}", response_model=TaskRecord)
async def get_task_status(task_id: str, db: AsyncSession = Depends(get_db)):
    query = select(TaskRecord).where(TaskRecord.task_id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "task_id": task.task_id,
        "status": task.status,
        "query": task.query,
        "result": task.result,
    }
