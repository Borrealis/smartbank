from enum import StrEnum
from uuid import UUID

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


class ComplianceSearchResult(BaseModel):
    source: str
    text: str
    source_url: str | None


class ComplianceSearchResponse(BaseModel):
    result: list[ComplianceSearchResult]


class ClientTariffInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    client_id: str = Field(
        min_length=8,
        max_length=14,
        description="Unique client identifier for example: client_abc",
    )


class WorkerStatus(StrEnum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ClientTariffSearchResult(BaseModel):
    client_id: str
    tariff: str | None
    status: str | None
    error: str | None


class GatewayRequest(BaseModel):
    task_id: UUID = Field(..., description="Unique task ideintifier")
    query: str = Field(..., description="User query text")


class WorkerResultPayload(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    confidence: float | None = None


class WorkerResponse(BaseModel):
    task_id: UUID
    status: WorkerStatus
    result: WorkerResultPayload | None = None


class ClientTariffInput(BaseModel):
    client_id: str = Field(..., description="Uniq client identifier")


class ComplianceSearchInput(BaseModel):
    search_query: str = Field(..., description="User search query to database")
    product_category: str | None = None
