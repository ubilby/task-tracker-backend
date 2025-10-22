from typing import Protocol, Optional
from domain.models.user import User


class UserRepository(Protocol):

    def save(self, user: User) -> User:
        ...

    def get_user(self, user_id: int) -> Optional[User]:
        ...

    def exists_by_nickname(self, nickname: str) -> bool:
        ...
