import pytest
from app.database import async_session
from app.models import Client
from app.tools import get_client_tariff_info

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_client_tariff_info_returns_data_for_existing_client():
    async with async_session() as session:
        client_66 = Client(id="client_66", tariff_plan="Premium", status="active")
        session.add(client_66)
        await session.commit()
    result = await get_client_tariff_info.ainvoke({"client_id": "client_66"})
    assert result.client_id == "client_66"
    assert result.tariff == "Premium"
    assert result.status == "active"
    assert result.error is None


async def test_get_client_tariff_info_returns_data_for_missing_client():
    fail_result = await get_client_tariff_info.ainvoke({"client_id": "client_99"})
    assert fail_result.client_id == "client_99"
    assert fail_result.tariff is None
    assert fail_result.status is None
    assert fail_result.error == "Client not found"
