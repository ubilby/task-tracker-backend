from pydantic import BaseModel
from typing import Optional
from application.dto.dtos import TaskCreateRawData


class TaskCreateRequest(TaskCreateRawData):
    ...


class TaskResponse(BaseModel):
    id: Optional[int]
    text: str
    done: bool

    class ConfigDict:
        from_attributes = True


class TaskUpdateStatusRequest(BaseModel):
    done: bool
