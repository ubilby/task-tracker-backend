from pydantic import BaseModel
from typing import Optional


# --- Запрос на создание задачи пользователем ---
class TaskCreateRequest(BaseModel):
    user_id: Optional[int]
    text: str


# --- Запрос на создание задачи ботом (для конкретного пользователя) ---
class TaskCreateForUserRequest(BaseModel):
    user_id: int
    text: str


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
