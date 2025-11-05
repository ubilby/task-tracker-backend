from user.domain.repository import User, UserRepository

class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register_user(self, telegram_id: int) -> User:
        if await self.user_repo.exists_by_telegram_id(telegram_id):
            raise ValueError("уже зарегестрирован")

        user = User(id=None, telegram_id=telegram_id)

        return await self.user_repo.save(user)

    async def get_user(self, id: int = 0) -> User:

        return await self.user_repo.get_user(id)

    async def delete_user(self, id: int) -> bool:

        return await self.user_repo.delete_user(id)
