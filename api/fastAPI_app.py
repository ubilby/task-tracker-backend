from fastapi import Depends, FastAPI, APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import List, Optional

from application.app import TaskTrackerApp, get_app_instance
from api.schemas.task import (
    TaskCreateRequest, TaskUpdateStatusRequest, TaskResponse, TaskCreateByAdminRequest
)
from api.schemas.user import UserCreateRequest, UserResponse, DeleteResponse

from dotenv import load_dotenv
from os import getenv

load_dotenv()


app = FastAPI(title="TaskTracker API")

user_router = APIRouter(prefix="/user", tags=["users"])
task_router = APIRouter(prefix="/task", tags=["tasks"])


BOT_TOKEN = getenv("BOT_TOKEN")


# ------------------- USERS -------------------

@user_router.post("/", response_model=UserResponse)
async def create_user(
    request: UserCreateRequest,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    is_bot = authorization == f"Bearer {BOT_TOKEN}"

    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    user = await tracker.users.register_user(nickname=request.nickname)

    return user


@user_router.delete("/{user_id}", response_model=DeleteResponse)
async def delete_user(
    user_id: int,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance),
):
    """Удаление пользователя (только для бота/админа)"""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"
    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    success = await tracker.users.delete_user(user_id)

    return DeleteResponse(success=success)

# ------------------- TASKS -------------------

@task_router.post("/", response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Создать задачу. Бот должен указать user_id, пользователь определяется по токену."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"

    # для пользователя: в будущем — определение по токену
    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

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

    # позже тут будет получение id пользователя из токена
    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

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

    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

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
    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    task = await tracker.tasks.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if request.done:
        task = await tracker.tasks.mark_done(task_id)
    else:
        task = await tracker.tasks.reopen(task_id)

    return task


@task_router.post("/user/{user_id}/task/", response_model=TaskResponse)
async def create_task_for_user(
    user_id: int,
    request: TaskCreateByAdminRequest,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance),
):
    """Бот создаёт новую задачу для пользователя (всегда со статусом done=False)."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"
    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    task = await tracker.tasks.create_task(
        user_id=user_id,
        text=request.text,
    )
    return task


@task_router.delete("task/{task_id}", response_model=DeleteResponse)
async def delete_task(
    task_id: int,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance),
):
    is_bot = authorization == f"Bearer {BOT_TOKEN}"
    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    success = await tracker.tasks.delete_task(task_id)

    return DeleteResponse(success=success)

# ------------------- REGISTER EXCEPTION HANDLER -------------------

@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc: ValueError):
    """
    Этот обработчик будет ловить ВСЕ ошибки ValueError,
    вылетающие из твоего приложения, и превращать их в 400 Bad Request.
    """
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


# ------------------- REGISTER ROUTERS -------------------

app.include_router(user_router)
app.include_router(task_router)
