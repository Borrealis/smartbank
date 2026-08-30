from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000, description="Query text")


class AskResponse(BaseModel):
    task_id: UUID = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status")


class WorkerResultPayload(BaseModel):
    answer: str = Field(..., description="Generated answe text")
    sources: list[str] = Field(
        default_factory=list, description=" List of source document Ids or links"
    )
    confidence: float | None = Field(default=None, description="Optional score or metadata")


class TaskStatusResponse(BaseModel):
    task_id: UUID = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status")
    model_config = ConfigDict(from_attributes=True)
    result: WorkerResultPayload | dict[str, Any] | None = Field(
        default=None, description="Structured task result"
    )
