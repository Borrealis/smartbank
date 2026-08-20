from uuid import UUID

from broker import kafka_router
from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import TaskRecord


class WorkerResponses(BaseModel):
    task_id: UUID = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status")
    result: str | None = Field(None, description="Task result(if task is ready)")


@kafka_router.subscriber("worker-responses")
async def get_task_info(m: WorkerResponses, db: AsyncSession = Depends(get_db)):
    query = select(TaskRecord).where(TaskRecord.task_id == m.task_id)
    result_db = await db.execute(query)
    result = m.result
    task = result_db.scalar_one_or_none()
    status = m.status

    if task is None:
        return

    task.status = status  # type: ignore
    task.result = result  # type: ignore
