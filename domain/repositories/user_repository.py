from typing import Protocol
from domain.models.user import User


class UserRepository(Protocol):

    async def save(self, user: User) -> User:
        ...

    async def get_user(self, user_id: int) -> User:
        ...

    # async def exists_by_nickname(self, nickname: str) -> bool:
    #     ...

    async def exists_by_telegram_id(self, telegram_id: int) -> bool:
        ...

    async def delete_user(self, id: int) -> bool:
        ...

    async def get_user_by_telegram_id(self, telegram_id: int) -> int:
        ...
