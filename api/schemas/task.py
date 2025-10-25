from pydantic import BaseModel, Field
from typing import Optional


class TaskCreateRequest(BaseModel):
    user_id: Optional[int]
    text: str


class TaskCreateByAdminRequest(BaseModel):
    text: str = Field(..., description="Текст задачи")


# --- Ответ API с задачей ---
class TaskResponse(BaseModel):
    id: Optional[int]
    text: str
    done: bool

    class ConfigDict:
        from_attributes = True


# --- Обновление статуса задачи ---
class TaskUpdateStatusRequest(BaseModel):
    done: bool
