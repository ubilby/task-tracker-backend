from typing import Optional

from pydantic import BaseModel

from domain.dto.dtos import TaskCreateRawData
from domain.models import User

class TaskCreateRequest(TaskCreateRawData):
    ...


class TaskResponse(BaseModel):
    id: Optional[int]
    text: str
    done: bool
    creator: User

    class ConfigDict:
        from_attributes = True


class TaskUpdateStatusRequest(BaseModel):
    done: bool
