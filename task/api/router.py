from os import getenv
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import Depends, APIRouter, Security, HTTPException
from fastapi.security import APIKeyHeader

from application.dependencies import get_app_instance, TaskTrackerApp, verify_bot_token
from user.api.schema import DeleteResponse
from task.api.schema import TaskCreateRequest, TaskResponse, TaskUpdateStatusRequest


load_dotenv()

task_router = APIRouter(
    prefix="/task",
    tags=["tasks"],
    dependencies=[Depends(verify_bot_token)]    
)

BOT_TOKEN = getenv("BOT_TOKEN")
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


@task_router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Создать задачу. Бот должен указать user_id, пользователь определяется по токену."""

    task = await tracker.tasks.create_task(request)

    return task


@task_router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    user_id: Optional[int] = None,
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Получить список задач пользователя (по user_id)."""

    if user_id is None:
        raise HTTPException(status_code=400, detail="user_id обязателен")

    tasks = await tracker.tasks.list_tasks(user_id)

    return tasks


@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Получить одну задачу по ID."""

    task = await tracker.tasks.get_task(task_id)

    return task


@task_router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: TaskUpdateStatusRequest,
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Изменить статус (или в будущем текст) задачи."""

    if request.done:
        task = await tracker.tasks.mark_done(task_id)
    else:
        task = await tracker.tasks.reopen(task_id)

    return task


@task_router.delete("/{task_id}", response_model=DeleteResponse)
async def delete_task(
    task_id: int,
    tracker: TaskTrackerApp = Depends(get_app_instance),
):
    success = await tracker.tasks.delete_task(task_id)

    return DeleteResponse(success=success)
