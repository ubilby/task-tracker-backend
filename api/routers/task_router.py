from fastapi import Depends, APIRouter, HTTPException, Header
from typing import List, Optional

from application.app import TaskTrackerApp, get_app_instance
from api.schemas.task import (
    TaskCreateRequest, TaskUpdateStatusRequest, TaskResponse
)
from api.schemas.user import DeleteResponse

from dotenv import load_dotenv
from os import getenv

load_dotenv()

task_router = APIRouter(prefix="/task", tags=["tasks"])

BOT_TOKEN = getenv("BOT_TOKEN")


@task_router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Создать задачу. Бот должен указать user_id, пользователь определяется по токену."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"

    #if not is_bot:
#        raise HTTPException(status_code=403, detail="Недостаточно прав")

    if not hasattr(request, "user_id") or request.user_id is None:
        raise HTTPException(status_code=400, detail="user_id обязателен для бота")

    task = await tracker.tasks.create_task(text=request.text, user_id=request.user_id)

    return task


@task_router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    user_id: Optional[int] = None,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Получить список задач пользователя (по user_id)."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"

    #if not is_bot:
#        raise HTTPException(status_code=403, detail="Недостаточно прав")

    if user_id is None:
        raise HTTPException(status_code=400, detail="user_id обязателен")

    tasks = await tracker.tasks.list_tasks(user_id)
    return tasks


@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Получить одну задачу по ID."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"

    #if not is_bot:
#        raise HTTPException(status_code=403, detail="Недостаточно прав")

    task = await tracker.tasks.get_task(task_id)
    return task


@task_router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: TaskUpdateStatusRequest,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Изменить статус (или в будущем текст) задачи."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"
    #if not is_bot:
#        raise HTTPException(status_code=403, detail="Недостаточно прав")

    task = await tracker.tasks.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if request.done:
        task = await tracker.tasks.mark_done(task_id)
    else:
        task = await tracker.tasks.reopen(task_id)

    return task


@task_router.delete("/{task_id}", response_model=DeleteResponse)
async def delete_task(
    task_id: int,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance),
):
    is_bot = authorization == f"Bearer {BOT_TOKEN}"
    #if not is_bot:
#        raise HTTPException(status_code=403, detail="Недостаточно прав")

    success = await tracker.tasks.delete_task(task_id)

    return DeleteResponse(success=success)
