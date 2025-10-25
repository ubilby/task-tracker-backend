from typing import Protocol, Optional
from domain.models.user import User


class UserRepository(Protocol):

    async def save(self, user: User) -> User:
        ...

    async def get_user(self, user_id: int) -> Optional[User]:
        ...

    async def exists_by_nickname(self, nickname: str) -> bool:
        ...

    async def delete_user(self, id: int) -> bool:
        ...