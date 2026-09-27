from faststream import FastStream
from faststream.kafka import KafkaBroker
from loguru import logger

from .agentic_loop import run_agentic_loop
from .config import settings
from .schemas import GatewayRequest, WorkerResponse, WorkerResultPayload, WorkerStatus

broker = KafkaBroker(settings.kafka_host)
app = FastStream(broker)


@broker.subscriber("gateway-request")
@broker.publisher("worker-response")
async def handle_gateway_request(msg: GatewayRequest):
    try:
        loop_result = await run_agentic_loop(msg.query)
        payload = WorkerResultPayload(answer=loop_result["answer"], sources=loop_result["sources"])
        response = WorkerResponse(
            task_id=msg.task_id, status=WorkerStatus.COMPLETED, result=payload
        )
    except Exception:
        logger.exception("Worker failed while handling task_id={}", msg.task_id)
        response = WorkerResponse(
            task_id=msg.task_id,
            status=WorkerStatus.FAILED,
            result=None,
        )

    return response
