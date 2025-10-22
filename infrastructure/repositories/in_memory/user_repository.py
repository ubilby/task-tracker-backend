from typing import List, Optional
from domain.models.user import User

from domain.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: List[User] = []
        self._next_id = 1

    def save(self, user: User) -> User:
        if user.id is None:
            user.id = self._next_id
            self._next_id +=1
            self._users.append(user)

        return user

    def get_user(self, user_id: int) -> Optional[User]:
        for user in self._users:
            if user.id == user_id:

                return user
        
        return None

    def exists_by_nickname(self, nickname: str) -> bool:
        return any(u.nickname == nickname for u in self._users)
