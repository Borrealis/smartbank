import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.kafka_handlers import WorkerResponses, get_task_info
from app.models import TaskRecord


@pytest.mark.asyncio
async def test_get_task_info_subscriber():
    db_mock = AsyncMock()
    shared_task_id = uuid4()

    mock_task = TaskRecord(
        task_id=shared_task_id, query="test query", status="PENDING", result=None
    )

    test_result_str = json.dumps({"data": "ok"})

    test_message = WorkerResponses(
        task_id=shared_task_id, status="COMPLETED", result=test_result_str
    )

    # Правильная настройка цепочки возврата
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    db_mock.execute.return_value = mock_result

    await get_task_info(m=test_message, db=db_mock)

    assert mock_task.status == "COMPLETED"
    assert mock_task.result == test_result_str
