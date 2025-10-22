from typing import Optional
from domain.models.user import User
from services.user_service import UserService


class UserApp:
    """Application layer для работы с пользователями."""

    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def register_user(self, nickname: str) -> User:
        return await self.user_service.register_user(nickname)

    async def get_user(self, id: int) -> Optional[User]:
        user: Optional[User] = await self.user_service.get_user(id)

        return user
