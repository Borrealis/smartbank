from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from app.broker import get_task_info
from app.models import TaskRecord
from app.schemas import TaskStatusResponse


@pytest.mark.asyncio
async def test_get_task_info_subscriber():
    db_mock = AsyncMock()
    shared_task_id = uuid4()
    mock_task = TaskRecord(
        task_id=shared_task_id, query="test query", status="PENDING", result=None
    )
    task_result_dict = {"answer": "test answer"}

    test_message = TaskStatusResponse(
        task_id=shared_task_id,
        status="COMPLETED",
        result=task_result_dict,  # type: ignore
    )

    # Правильная настройка цепочки возврата
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    db_mock.execute.return_value = mock_result

    await get_task_info(msg=test_message, db=db_mock)

    assert mock_task.status == "COMPLETED"
    assert mock_task.result == {"answer": "test answer", "sources": [], "confidence": None}
    db_mock.commit.assert_awaited_once()
