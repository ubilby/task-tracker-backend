from typing import List, Optional
from domain.models.user import User

from domain.repositories.user_repository import UserRepository

users: List[User] = []
next_id: List[int] = [1]

class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: List[User] = []
        self._next_id = 1

    async def save(self, user: User) -> User:
        if user.id is None:
            user.id = next_id[0]
            next_id[0] += 1
            users.append(user)

        return user

    async def get_user(self, user_id: int) -> Optional[User]:
        for user in users:
            if user.id == user_id:

                return user

        return None

    async def exists_by_nickname(self, nickname: str) -> bool:
        return any(u.nickname == nickname for u in users)
