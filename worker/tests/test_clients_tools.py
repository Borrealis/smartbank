import pytest
from app.tools import get_client_tariff_info

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_client_tariff_info_returns_data_for_existing_client():
    result = await get_client_tariff_info.ainvoke({"client_id": "client_66"})
    assert result == {
        "client_id": "client_66",
        "tariff": "Premium",
        "status": "active",
        "error": None,
    }


async def test_get_client_tariff_info_returns_data_for_missing_client():
    fail_result = await get_client_tariff_info.ainvoke({"client_id": "client_99"})
    assert fail_result == {
        "client_id": "client_99",
        "tariff": None,
        "status": None,
        "error": "Client not found",
    }
