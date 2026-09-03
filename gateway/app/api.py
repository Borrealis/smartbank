from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .broker import publish_ask_request
from .database import get_db
from .models import TaskRecord
from .schemas import AskRequest, AskResponse, TaskStatusResponse

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_question(requests: AskRequest, db: AsyncSession = Depends(get_db)):
    task_id = requests.task_id
    new_task = TaskRecord(task_id=task_id, query=requests.query, status="PENDING")
    db.add(new_task)
    try:
        await publish_ask_request(requests)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=503, detail="Service temporaly not awailable now. Task not send in worker "
        ) from e
    return {"task_id": requests.task_id, "status": "PENDING"}


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(TaskRecord).where(TaskRecord.task_id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Not found")
    return task
