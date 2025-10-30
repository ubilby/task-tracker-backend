from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.repositories.user_repository import UserRepository
from domain.models.user import User
from infrastructure.db.models import DBUser


class SQLAlchemyUserRepository(UserRepository):
    """Реализация репозитория пользователя через SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user: User) -> User:
        """Сохраняет или обновляет пользователя в базе данных."""
        if user.id is None:
            # Создание нового пользователя
            db_user = DBUser(telegram_id=user.telegram_id)
            self.session.add(db_user)
            await self.session.flush()
            await self.session.refresh(db_user)
            user = User(id=db_user.id, telegram_id=db_user.telegram_id)
        else:
            # Обновление существующего пользователя
            db_user = await self.session.get(DBUser, user.id)
            if db_user:
                # В текущей модели обновлять нечего, но commit всё равно нужен для целостности
                pass 
        
        await self.session.commit() # <-- ДОБАВЛЕН COMMIT
        return user

    async def get_user(self, user_id: int) -> User:
        """Получает пользователя по внутреннему ID."""
        db_user = await self.session.get(DBUser, user_id)
        
        if db_user is None:
            raise ValueError("Пользователь не найден")
                    
        return User(
            id=db_user.id,
            telegram_id=db_user.telegram_id
        )

    async def exists_by_telegram_id(self, telegram_id: int) -> bool:
        """Проверяет существование пользователя по telegram_id."""
        stmt = select(DBUser.id).where(DBUser.telegram_id == telegram_id)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def get_user_by_telegram_id(self, telegram_id: int) -> int:
        """Получает внутренний ID пользователя по telegram_id."""
        stmt = select(DBUser.id).where(DBUser.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user_id = result.scalar_one_or_none()

        if user_id is None:
            raise ValueError("Пользователь по telegram_id не найден")

        return user_id

    async def delete_user(self, id: int) -> bool:
        """Удаляет пользователя по ID."""
        db_user = await self.session.get(DBUser, id)

        if db_user:
            await self.session.delete(db_user)
            await self.session.flush()
            await self.session.commit() # <-- ДОБАВЛЕН COMMIT
            return True

        return False
