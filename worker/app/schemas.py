from pydantic import BaseModel, ConfigDict, Field


class SearchComplianceTool(BaseModel):
    model_config = ConfigDict(extra="forbid")
    search_query: str = Field(
        min_length=1,
        max_length=1000,
        description="Search query to retrieve compliance and regulatory documents from vector base",
    )
    product_category: str | None = Field(
        default=None,
        description="Optional product category for "
        "filtration (for example: money transfers, current accounts)",
    )


class ClientTariffInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    client_id: str = Field(
        min_length=8,
        max_length=14,
        description="Unique client identifier for example: client_abc",
    )


# class GetClientTariffInfo:
