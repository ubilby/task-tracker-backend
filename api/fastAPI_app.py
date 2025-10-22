from fastapi import Depends, FastAPI, APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import List, Optional

from application.app import TaskTrackerApp, get_app_instance
from api.schemas.task import TaskCreateRequest, TaskUpdateStatusRequest, TaskResponse
from api.schemas.user import UserCreateRequest, UserResponse

from dotenv import load_dotenv
from os import getenv

load_dotenv()


app = FastAPI(title="TaskTracker API")

user_router = APIRouter(prefix="/user", tags=["users"])
task_router = APIRouter(prefix="/task", tags=["tasks"])


BOT_TOKEN = getenv("BOT_TOKEN")


# ------------------- USERS -------------------

@user_router.post("/", response_model=UserResponse)
def create_user(
    request: UserCreateRequest,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    is_bot = authorization == f"Bearer {BOT_TOKEN}"

    if is_bot:
        return tracker.users.register_user(nickname=request.nickname)

    
    return JSONResponse(status_code=400, content={"detail": "no permission"})


# ------------------- TASKS -------------------

@task_router.post("/", response_model=TaskResponse)
def create_task(
    request: TaskCreateRequest,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Создать задачу. Бот должен указать user_id, пользователь определяется по токену."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"

    if not is_bot:
        # для пользователя: в будущем — определение по токену
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    if not hasattr(request, "user_id") or request.user_id is None:
        raise HTTPException(status_code=400, detail="user_id обязателен для бота")

    # user = tracker.users.get_user(request.user_id)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")

    return tracker.tasks.create_task(text=request.text, user_id=request.user_id)


@task_router.get("/", response_model=List[TaskResponse])
def list_tasks(
    user_id: Optional[int] = None,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Получить список задач пользователя (по user_id)."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"

    if not is_bot:
        # позже тут будет получение id пользователя из токена
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    if user_id is None:
        raise HTTPException(status_code=400, detail="user_id обязателен")

    # user = tracker.users.get_user(user_id)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")

    return tracker.tasks.list_tasks(user_id)


@task_router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    """Получить одну задачу по ID."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"
    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    return tracker.tasks.get_task(task_id)
    # if not task:
    #     raise HTTPException(status_code=404, detail="Task not found")


@task_router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    request: TaskUpdateStatusRequest,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
    ):
    """Изменить статус (или в будущем текст) задачи."""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"
    if not is_bot:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    task = tracker.tasks.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if request.done:
        task = tracker.tasks.mark_done(task_id)
    else:
        task = tracker.tasks.reopen(task_id)

    return task


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

