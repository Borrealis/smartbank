from uuid import uuid4

import pytest
from app.broker import kafka_router
from app.main import app
from fastapi.testclient import TestClient
from faststream.kafka import TestKafkaBroker
from httpx import ASGITransport, AsyncClient

client = TestClient(app)


@pytest.mark.asyncio
async def test_ask_question_kafak_rollback(override_db, monkeypatch):
    async def falling_publish(message):
        raise Exception("Kafka is down")

    monkeypatch.setattr("app.api.publish_ask_request", falling_publish)
    payload = {"query": "test_query"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/ask", json=payload)
    assert response.status_code == 503
    override_db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_ask_question(override_db):
    payload = {"query": "How transfer money to IP  without fee"}
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
