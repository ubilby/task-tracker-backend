from domain.repositories.user_repository import UserRepository
from domain.models.user import User

class UserService:

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def register_user(self, nickname: str) -> User:
        if self.user_repo.exists_by_nickname(nickname):
            raise ValueError("Nickname уже занят")

        user = User(id=None, nickname=nickname)

        return self.user_repo.save(user)
