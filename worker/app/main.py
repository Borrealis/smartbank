from uuid import UUID

from faststream import FastStream
from faststream.kafka import KafkaBroker
from pydantic import BaseModel, Field

from .dispatcher import run_agentic_loop


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


broker = KafkaBroker("localhost:9092")
app = FastStream(broker)


@broker.publisher("worker-response")
async def publish_worker_response(response: WorkerResponse):
    return response


@broker.subscriber("gateway-request")
async def handle_gateway_request(msg: GatewayRequest):
    loop_result = await run_agentic_loop(msg.query)
    payload = WorkerResultPayload(answer=loop_result["answer"], sources=["test_doc"])
    response = WorkerResponse(task_id=msg.task_id, status="COMPLETED", result=payload)
    await publish_worker_response(response)
