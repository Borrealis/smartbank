from langchain_core.tools import tool
from pydantic import BaseModel, Field


class ClientTariffInput(BaseModel):
    client_id: str = Field(..., description="Uniq client identifier")


class ComplianceSearchInput(BaseModel):
    search_query: str = Field(..., description="User search query to database")
    product_category: str | None = None


@tool(args_schema=ClientTariffInput)
def get_client_tariff_info(client_id: str) -> str:
    mock_db = {
        "client_123": {"tariff": "Premium", "status": "active"},
        "client_S934": {"tariff": "Base", "status": "active"},
        "client_ff94": {"tariff": "Diamond", "status": "blocked"},
    }
    client_data = mock_db.get(client_id, "Standart")
    if not client_data:
        return f"Client with {client_id} not found in base"
    return f"Current client tariff {client_data}"


@tool(args_schema=ComplianceSearchInput)
def search_compliance_knowledge(search_query: str, product_category: str | None = None) -> str:
    filter_info = f" with category filter: '{product_category}'" if product_category else ""
    return f"Found documents for query: '{search_query}'{filter_info}"
