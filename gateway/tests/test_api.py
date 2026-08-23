from uuid import uuid4

from app.api import get_db
from app.broker import kafka_router
from app.main import app
from fastapi.testclient import TestClient
from faststream.kafka import TestKafkaBroker

client = TestClient(app)


def test_ask_question():
    payload = {"query": "How transfer money to IP  without fee"}

    async def run_test():
        with TestKafkaBroker(kafka_router.broker):  # type: ignore
            with client:
                response = client.post("/ask", json=payload)
                data = response.json()
                assert "task_id" in data
                assert response.status_code == 200
                assert data["status"] == "PENDING"
        import asyncio

        asyncio.run(run_test())


async def override_dependency():
    class MockResult:
        def scalar_one_or_none(self):
            return None

    class MockSession:
        async def execute(self, query):
            return MockResult()

    yield MockSession()


def test_get_status_not_found():
    app.dependency_overrides[get_db] = override_dependency
    fake_id = uuid4()
    response = client.get(f"/status/{fake_id}")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    task_data = response.json()
    assert "detail" in task_data

    # def test_get_status_not_found():


#     fake_id = uuid4()

#     response = client.get(f"/status/{fake_id}")
#     assert response.status_code == 404
#     task_data = response.json()
#     assert "detail" in task_data
