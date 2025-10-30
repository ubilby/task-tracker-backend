from os import getenv, path
from sys import path as syspath
syspath.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from domain.models.user import User
from domain.models.task import Task
from infrastructure.db.database import engine
from infrastructure.db.models import Base
from infrastructure.repositories.sqlalchemy.user_repository import SQLAlchemyUserRepository
from infrastructure.repositories.sqlalchemy.task_repository import SQLAlchemyTaskRepository


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Создает все таблицы в начале тестовой сессии."""
    async with engine.begin() as conn:
        # Удаляем и создаем все таблицы для чистой среды
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию для каждого теста.
    Каждый тест выполняется в транзакции, которая откатывается (rollback) после завершения,
    обеспечивая изоляцию.
    
    ИСПРАВЛЕНИЕ: Заменено engine.begin() на engine.connect(), чтобы избежать
    конфликта из-за двойного вызова begin().
    """
    # 1. Используем engine.connect(), чтобы получить "чистое" соединение без неявной транзакции.
    async with engine.connect() as connection:
        # 2. Теперь явно начинаем корневую транзакцию для теста.
        # Это предотвращает InvalidRequestError.
        transaction = await connection.begin()
        
        # 3. Создаем асинхронную сессию, привязанную к этому соединению/транзакции.
        async_session = AsyncSession(
            bind=connection, expire_on_commit=False, autoflush=False
        )
        
        # 4. В SQLAlchemy 2.0+ сессия, привязанная к активной транзакции, не требует 
        # дополнительного вызова async_session.begin().

        yield async_session

        # 5. Очистка: закрываем сессию и откатываем транзакцию, чтобы отменить все изменения.
        # transaction.rollback() откатывает транзакцию, начатую на connection.begin().
        await async_session.close()
        await transaction.rollback()


@pytest_asyncio.fixture # <-- Использован pytest_asyncio.fixture
async def user_repo(db_session: AsyncSession) -> SQLAlchemyUserRepository:
    """Фикстура для UserRepository."""
    return SQLAlchemyUserRepository(db_session)


@pytest_asyncio.fixture # <-- Использован pytest_asyncio.fixture
async def task_repo(db_session: AsyncSession) -> SQLAlchemyTaskRepository:
    """Фикстура для TaskRepository."""
    return SQLAlchemyTaskRepository(db_session)


@pytest.mark.asyncio
class TestSQLAlchemyUserRepository:
    """Тесты для SQLAlchemyUserRepository."""

    async def test_1(self, user_repo, task_repo):
        assert 1

    async def test_save_new_user(self, user_repo: SQLAlchemyUserRepository):
        """Проверяет сохранение нового пользователя и генерацию ID."""
        telegram_id = 90001
        new_user = User(id=None, telegram_id=telegram_id)
        
        saved_user = await user_repo.save(new_user)
        
        assert saved_user.id is not None
        assert saved_user.telegram_id == telegram_id
        # Проверяем, что пользователь действительно в базе
        fetched_user = await user_repo.get_user(saved_user.id)
        assert fetched_user.telegram_id == telegram_id

    async def test_get_nonexistent_user(self, user_repo: SQLAlchemyUserRepository):
        """Проверяет получение несуществующего пользователя."""
        with pytest.raises(ValueError):
            user = await user_repo.get_user(999999)
            assert user is None

    async def test_duplicate_telegram_id_raises_error(self, user_repo: SQLAlchemyUserRepository):
        """Проверяет ограничение уникальности telegram_id."""
        telegram_id = 90002
        await user_repo.save(User(id=None, telegram_id=telegram_id))
        
        # Попытка сохранить второго пользователя с тем же telegram_id
        with pytest.raises(IntegrityError):
            await user_repo.save(User(id=None, telegram_id=telegram_id))
    
    async def test_exists_by_telegram_id(self, user_repo: SQLAlchemyUserRepository):
        """Проверяет метод exists_by_telegram_id."""
        telegram_id = 90003
        await user_repo.save(User(id=None, telegram_id=telegram_id))

        assert await user_repo.exists_by_telegram_id(telegram_id) is True
        assert await user_repo.exists_by_telegram_id(999999) is False

    async def test_delete_user(self, user_repo: SQLAlchemyUserRepository):
        """Проверяет удаление пользователя."""
        user_to_delete = await user_repo.save(User(id=None, telegram_id=90004))
        assert user_to_delete.id
        # Удаляем
        success = await user_repo.delete_user(user_to_delete.id)
        assert success is True
        
        # Проверяем, что он действительно удален
        with pytest.raises(ValueError):
            user = await user_repo.get_user(user_to_delete.id)
        
        # # Проверяем удаление несуществующего
        assert not (await user_repo.delete_user(9999991))

    async def test_get_user_id_by_telegram_id(self, user_repo: SQLAlchemyUserRepository):
        """Проверяет получение внутреннего ID по Telegram ID."""
        telegram_id = 90005
        user = await user_repo.save(User(id=None, telegram_id=telegram_id))

        fetched_id = await user_repo.get_user_by_telegram_id(telegram_id)
        assert fetched_id == user.id
        with pytest.raises(ValueError):
            assert await user_repo.get_user_by_telegram_id(999999) is None


@pytest.mark.asyncio
class TestSQLAlchemyTaskRepository:
    """Тесты для SQLAlchemyTaskRepository."""

    @pytest_asyncio.fixture
    async def setup_user(self, user_repo: SQLAlchemyUserRepository) -> User:
        """Создает и возвращает тестового пользователя для задач."""
        return await user_repo.save(User(id=None, telegram_id=88888))

    async def test_save_new_task(self, task_repo: SQLAlchemyTaskRepository, setup_user: User):
        """Проверяет создание и сохранение новой задачи."""
        new_task = Task(id=None, text="Купить молоко", creator=setup_user)
        saved_task = await task_repo.save(new_task)

        assert saved_task.id is not None
        assert saved_task.text == "Купить молоко"
        assert saved_task.done is False
        assert saved_task.creator.id == setup_user.id

        # Проверяем, что задача в базе
        fetched_task = await task_repo.get_by_id(saved_task.id)
        assert fetched_task
        assert fetched_task.id == saved_task.id
        assert fetched_task.creator.telegram_id == setup_user.telegram_id # Проверка маппинга связи

    async def test_update_task_status(self, task_repo: SQLAlchemyTaskRepository, setup_user: User):
        """Проверяет обновление статуса задачи."""
        task = await task_repo.save(Task(id=None, text="Позвонить маме", creator=setup_user))
        
        # Отмечаем как выполненную
        task.mark_done()
        updated_task = await task_repo.save(task)
        
        assert updated_task.done is True
        
        # Проверяем в базе
        assert task.id
        fetched_task = await task_repo.get_by_id(task.id)
        assert fetched_task
        assert fetched_task.done is True

    async def test_list_tasks_by_user(
        self, 
        task_repo: SQLAlchemyTaskRepository, 
        user_repo: SQLAlchemyUserRepository, 
        setup_user: User
    ):
        """Проверяет получение списка задач для пользователя."""
        user2 = await user_repo.save(User(id=None, telegram_id=88889))

        # Задачи для setup_user
        await task_repo.save(Task(id=None, text="Задача 1", creator=setup_user))
        await task_repo.save(Task(id=None, text="Задача 2", creator=setup_user))
        # Задача для user2
        await task_repo.save(Task(id=None, text="Задача User2", creator=user2))

        tasks_user1 = await task_repo.list_by_user(setup_user)
        tasks_user2 = await task_repo.list_by_user(user2)

        assert len(tasks_user1) == 2
        assert len(tasks_user2) == 1
        assert tasks_user1[0].text == "Задача 1"
        assert tasks_user1[1].text == "Задача 2"

    async def test_delete_task(self, task_repo: SQLAlchemyTaskRepository, setup_user: User):
        """Проверяет удаление задачи."""
        task_to_delete: Task = await task_repo.save(Task(id=None, text="Удалить меня", creator=setup_user))
        assert task_to_delete.id
        success = await task_repo.delete_task(task_to_delete.id)
        assert success is True

        with pytest.raises(ValueError):
            assert await task_repo.get_by_id(task_to_delete.id) # is None
            assert await task_repo.delete_task(999999) # is False
