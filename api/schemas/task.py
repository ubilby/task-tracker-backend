from pydantic import BaseModel, Field
from typing import Optional


class TaskCreateRequest(BaseModel):
    user_id: Optional[int]
    text: str


class TaskResponse(BaseModel):
    id: Optional[int]
    text: str
    done: bool

    class ConfigDict:
        from_attributes = True


class TaskUpdateStatusRequest(BaseModel):
    done: bool
