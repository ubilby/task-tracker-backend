from typing import Optional
from domain.repositories.user_repository import UserRepository
from domain.models.user import User


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register_user(self, nickname: str) -> User:
        if await self.user_repo.exists_by_nickname(nickname):
            raise ValueError("Nickname уже занят")

        user = User(id=None, nickname=nickname)

        return await self.user_repo.save(user)

    async def get_user(self, id: int = 0) -> Optional[User]:

        return await self.user_repo.get_user(id)
