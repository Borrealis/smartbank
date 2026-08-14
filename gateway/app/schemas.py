from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000, description="Query text")


class AskResponse(BaseModel):
    task_id: UUID = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status")


class TaskStatusResponse(BaseModel):
    task_id: UUID = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status")
    result: str | None = Field(None, description="Task result(if task is ready)")
    model_config = ConfigDict(from_attributes=True)
