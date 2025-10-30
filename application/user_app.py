from domain.dto.dtos import RegisterUserDTO
from domain.models.user import User
from services.user_service import UserService


class UserApp:
    """Application layer для работы с пользователями."""

    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def register_user(self, data: RegisterUserDTO) -> User:
        return await self.user_service.register_user(data.telegram_id)

    async def get_user(self, id: int) -> User:
        user: User = await self.user_service.get_user(id)

        return user

    async def delete_user(self, id: int) -> bool:
        result: bool = await self.user_service.delete_user(id)

        return result
