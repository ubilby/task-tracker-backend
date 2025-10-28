from typing import List
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
            user.id = self._next_id
            self._next_id += 1
            self._users.append(user)

        return user

    async def get_user(self, user_id: int) -> User:
        for user in self._users:
            if user.id == user_id:

                return user

        # добавить свою ошибку
        raise ValueError("Пользователь не найден")

    # async def exists_by_nickname(self, nickname: str) -> bool:

    #     return any(user.nickname == nickname for user in self._users)

    async def exists_by_telegram_id(self, telegram_id: int) -> bool:
        return any(user.telegram_id == telegram_id for user in self._users)

    async def delete_user(self, id: int) -> bool:
        index = -1

        for i, user in enumerate(self._users):
            if user.id == id:
                index = i
                break

        if index != -1:
            users.pop(index)

            return True

        return False

    async def get_user_by_telegram_id(self, telegram_id: int) -> int:
        for user in self._users:
            if user.telegram_id == telegram_id and user.id:

                return user.id
            
        raise Exception
