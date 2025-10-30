from dotenv import load_dotenv
from os import getenv

from fastapi import APIRouter, Depends, Header, HTTPException

from application.app import TaskTrackerApp, get_app_instance
from api.schemas.user import DeleteResponse, UserCreateRequest, UserResponse
from domain.models.user import User


load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")

user_router = APIRouter(prefix="/user", tags=["users"])


@user_router.post("/", response_model=UserResponse)
async def create_user(
    request: UserCreateRequest,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    is_bot = authorization == f"Bearer {BOT_TOKEN}"
    # there will some authorization logic
    #if not is_bot:
#        raise HTTPException(status_code=403, detail="Недостаточно прав")
    user: User = await tracker.users.register_user(request)
    return user


@user_router.delete("/{user_id}", response_model=DeleteResponse)
async def delete_user(
    user_id: int,
    authorization: str = Header(None),
    tracker: TaskTrackerApp = Depends(get_app_instance),
):
    """Удаление пользователя (только для бота/админа)"""
    is_bot = authorization == f"Bearer {BOT_TOKEN}"
    #if not is_bot:
#        raise HTTPException(status_code=403, detail="Недостаточно прав")

    success = await tracker.users.delete_user(user_id)

    return DeleteResponse(success=success)
