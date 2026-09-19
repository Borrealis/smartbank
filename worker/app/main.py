import logging
from uuid import UUID

from faststream import FastStream
from faststream.kafka import KafkaBroker
from pydantic import BaseModel, Field

from .agentic_loop import run_agentic_loop
from .config import settings

logger = logging.getLogger(__name__)


class GatewayRequest(BaseModel):
    task_id: UUID = Field(..., description="Unique task ideintifier")
    query: str = Field(..., description="User query text")


class WorkerResultPayload(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    confidence: float | None = None


class WorkerResponse(BaseModel):
    task_id: UUID
    status: str
    result: WorkerResultPayload | None = None


broker = KafkaBroker(settings.kafka_host)
app = FastStream(broker)


worker_response_publisher = broker.publisher("worker-response")


@broker.subscriber("gateway-request")
async def handle_gateway_request(msg: GatewayRequest):
    try:
        loop_result = await run_agentic_loop(msg.query)
        payload = WorkerResultPayload(answer=loop_result["answer"], sources=loop_result["sources"])
        response = WorkerResponse(task_id=msg.task_id, status="COMPLETED", result=payload)
    except Exception:
        logger.exception("Worker failed while handling task_id=%s", msg.task_id)
        response = WorkerResponse(
            task_id=msg.task_id,
            status="FAILED",
            result=None,
        )

    await worker_response_publisher.publish(response)
