from typing import Optional

from pydantic import BaseModel

from domain.dto.dtos import TaskCreateRawData


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
