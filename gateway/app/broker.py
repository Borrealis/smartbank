from fastapi import Depends
from faststream.kafka.fastapi import KafkaRouter
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_db
from .models import TaskRecord
from .schemas import AskRequest, TaskStatusResponse, WorkerResultPayload

kafka_router = KafkaRouter(settings.kafka_host)


@kafka_router.publisher("gateway-request")
async def publish_ask_request(msg: AskRequest) -> AskRequest:
    """Публикация задачи в Kafka топик gateway-request."""
    logger.info("Publishing task to Kafka: task_id={}", msg.task_id)
    return msg


@kafka_router.subscriber("worker-response")
async def get_task_info(msg: TaskStatusResponse, db: AsyncSession = Depends(get_db)):
    """Обработка ответа от воркера и обновление статуса задачи в БД."""
    logger.info("Received worker response: task_id={}, status={}", msg.task_id, msg.status)
    try:
        query = select(TaskRecord).where(TaskRecord.task_id == msg.task_id)
        result_db = await db.execute(query)
        task = result_db.scalar_one_or_none()

        if task is None:
            logger.warning("Task with id {} not found in database", msg.task_id)
            return

        task.status = msg.status
        task.result = (
            msg.result.model_dump() if isinstance(msg.result, WorkerResultPayload) else msg.result
        )
        await db.commit()
        logger.info("Task {} successfully updated in DB", msg.task_id)
    except Exception:
        logger.exception("Failed to process task update for task_id={}", msg.task_id)
