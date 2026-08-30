from uuid import UUID

from fastapi import Depends
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .broker import kafka_router
from .database import get_db
from .models import TaskRecord
from .schemas import WorkerResultPayload


class WorkerResponse(BaseModel):
    task_id: UUID = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status")
    result: WorkerResultPayload | None = Field(None, description="Task result(if task is ready")


@kafka_router.subscriber("worker-response")
async def get_task_info(m: WorkerResponse, db: AsyncSession = Depends(get_db)):
    try:
        query = select(TaskRecord).where(TaskRecord.task_id == m.task_id)
        result_db = await db.execute(query)
        task = result_db.scalar_one_or_none()

        if task is None:
            logger.error(f"Task with id {m.task_id} not found in database")
            return
        task.status = m.status

        task.result = m.result.model_dump() if m.result is not None else None

    except Exception:
        logger.exception(f"Failed to process task update for task_id={m.task_id}")
