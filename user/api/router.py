from dotenv import load_dotenv
from os import getenv

from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyHeader

from application.dependencies import TaskTrackerApp, get_app_instance, verify_bot_token
from user.api.schema import DeleteResponse, UserCreateRequest, UserResponse
from user.domain.model import User


load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

user_router = APIRouter(
    prefix="/user",
    tags=["users"],
    dependencies=[Depends(verify_bot_token)]    

)


@user_router.post("/", response_model=UserResponse)
async def create_user(
    request: UserCreateRequest,
    tracker: TaskTrackerApp = Depends(get_app_instance)
):
    user: User = await tracker.users.register_user(request)
    return user


@user_router.delete("/{user_id}", response_model=DeleteResponse)
async def delete_user(
    user_id: int,
    tracker: TaskTrackerApp = Depends(get_app_instance),
):
    """Удаление пользователя (только для бота/админа)"""
    success = await tracker.users.delete_user(user_id)

    return DeleteResponse(success=success)
