from dotenv import load_dotenv
from os import getenv

from fastapi import Depends, APIRouter, HTTPException, Header

from application.app import TaskTrackerApp, get_app_instance
from api.schemas.user import UserCreateRequest, UserResponse, DeleteResponse

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

    #if not is_bot:
#        raise HTTPException(status_code=403, detail="Недостаточно прав")

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
    #if not is_bot:
#        raise HTTPException(status_code=403, detail="Недостаточно прав")

    success = await tracker.users.delete_user(user_id)

    return DeleteResponse(success=success)
