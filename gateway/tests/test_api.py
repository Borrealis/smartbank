from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from app.broker import kafka_router
from app.main import app
from app.models import TaskRecord
from fastapi.testclient import TestClient
from faststream.kafka import TestKafkaBroker
from httpx import ASGITransport, AsyncClient

client = TestClient(app)

completed_task = TaskRecord(
    task_id=uuid4,
    query="test query",
    status="COMPLETED",
    result={"answer": "test answer", "sources": ["docs/test.md"], "confidence": None},
)


@pytest.mark.asyncio
async def test_ask_question_kafka(override_db, monkeypatch):
    async def failing_publish(message):
        raise Exception("Kafka is down")

    monkeypatch.setattr("app.api.gateway_request_publisher.publish", failing_publish)
    payload = {"query": "test_query"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/ask", json=payload)
    assert response.status_code == 503
    assert response.json()["detail"] == "Failed send task to Kafka"
    created_task = override_db.add.call_args.args[0]
    assert created_task.status == "FAILED"
    assert override_db.commit.await_count == 2


@pytest.mark.asyncio
async def test_ask_question(override_db):
    payload = {"query": "How transfer money to IP without fee"}
    async with TestKafkaBroker(kafka_router.broker):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/ask", json=payload)
            data = response.json()
            assert "task_id" in data
            assert response.status_code == 200
            assert data["status"] == "PENDING"


def test_get_status_not_found(override_db):
    fake_id = uuid4()
    response = client.get(f"/status/{fake_id}")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    task_data = response.json()
    assert "detail" in task_data


def test_get_success_status(override_db):
    task_id = uuid4()
    completed_task = TaskRecord(
        task_id=task_id,
        query="test query",
        status="COMPLETED",
        result={
            "answer": "test answer",
            "sources": ["docs/test.md"],
            "confidence": None,
        },
    )

    query_result = MagicMock()
    query_result.scalar_one_or_none.return_value = completed_task
    override_db.execute.return_value = query_result

    response = client.get(f"/status/{task_id}")

    assert response.status_code == 200

    task_data = response.json()
    assert task_data["task_id"] == str(task_id)
    assert task_data["status"] == "COMPLETED"
    assert task_data["result"]["answer"] == "test answer"
    assert task_data["result"]["sources"] == ["docs/test.md"]
