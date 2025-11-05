from os import getenv, path
from sys import path as syspath
syspath.insert(0, path.abspath(path.join(path.dirname(__file__), '..')))

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from task.domain.model import Task, User
from task.dto import TaskCreateRawData
from user.sql_repository import SQLAlchemyUserRepository
from task.sql_repository import SQLAlchemyTaskRepository
from infrastructure.db.database import engine
from user.service import UserService
from task.service import TaskService


@pytest.fixture
def user_repo_real(db_session: AsyncSession) -> SQLAlchemyUserRepository:
    """Фикстура, предоставляющая реальный SQLAlchemyUserRepository."""
    return SQLAlchemyUserRepository(db_session)


@pytest.fixture
def task_repo_real(db_session: AsyncSession) -> SQLAlchemyTaskRepository:
    """Фикстура, предоставляющая реальный SQLAlchemyTaskRepository."""
    return SQLAlchemyTaskRepository(db_session)


@pytest.fixture
def user_service_integration(user_repo_real: SQLAlchemyUserRepository) -> UserService:
    """Фикстура, предоставляющая UserService с реальным репозиторием."""
    return UserService(user_repo_real)


@pytest.fixture
def task_service_integration(
    task_repo_real: SQLAlchemyTaskRepository, 
    user_repo_real: SQLAlchemyUserRepository
) -> TaskService:
    """Фикстура, предоставляющая TaskService с реальными репозиториями."""
    return TaskService(task_repo_real, user_repo_real)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию для каждого теста, используя savepoint.
    """
    # 1. Получаем соединение
    async with engine.connect() as connection:
        # 2. Начинаем корневую транзакцию (для фиксации/отката всех изменений)
        async with connection.begin():
            
            # 3. Создаем сессию, привязанную к соединению
            async_session = AsyncSession(
                bind=connection, expire_on_commit=False, autoflush=False
            )
            
            # 4. Начинаем вложенную транзакцию (это savepoint)
            # Вложенная транзакция откатывается автоматически при закрытии сессии.
            async with async_session.begin():
                yield async_session
                
            # 5. Откатываем корневую транзакцию после теста
            # Откат корневой транзакции гарантирует, что все изменения отменены.
            # Если тест успешно завершил свою работу (yield), мы явно откатываем
            # чтобы избежать фиксации данных.
            await connection.rollback() # <-- Явный rollback корневой транзакции
            
            # 6. Закрываем сессию
            await async_session.close()

# --- Тесты ---

@pytest.mark.asyncio
class TestUserServiceIntegration:
    """Интеграционные тесты для UserService с реальным DB репозиторием."""

    async def test_register_and_get_user(self, user_service_integration: UserService):
        """Проверяет регистрацию через сервис и последующее получение."""
        telegram_id = 1234567

        # 1. Вызов бизнес-логики (регистрация)
        new_user = await user_service_integration.register_user(telegram_id)

        assert new_user.id is not None
        assert new_user.telegram_id == telegram_id

        # 2. Проверяем получение пользователя по ID (второй вызов сервиса)
        fetched_user = await user_service_integration.get_user(new_user.id)
        assert fetched_user.telegram_id == telegram_id
        
        # 3. Проверяем, что дубликат вызывает ошибку
        with pytest.raises(ValueError, match="уже зарегестрирован"):
            await user_service_integration.register_user(telegram_id)

    async def test_get_non_existent_user_raises_error(self, user_service_integration: UserService):
        """Проверяет, что сервис корректно обрабатывает ошибку 'не найдено'."""
        with pytest.raises(ValueError, match="Пользователь не найден"):
            await user_service_integration.get_user(999)


@pytest.mark.asyncio
class TestTaskServiceIntegration:
    """Интеграционные тесты для TaskService с реальными DB репозиториями."""

    @pytest_asyncio.fixture
    async def registered_user(self, user_service_integration: UserService) -> User:
        """Создает и сохраняет пользователя, необходимого для тестов задач."""
        # Используем сервис для создания пользователя
        return await user_service_integration.register_user(telegram_id=9876543)

    async def test_create_task(self, task_service_integration: TaskService, registered_user: User):
        """Проверяет создание задачи через сервис."""
        assert registered_user.id is not None
        dto = TaskCreateRawData(user_id=registered_user.id, text="Купить молоко")
        
        task = await task_service_integration.create_task(dto)

        assert task.id is not None
        assert task.text == "Купить молоко"
        assert task.creator.id == registered_user.id

    async def test_create_task_for_non_existent_user(self, task_service_integration: TaskService):
        """Проверяет, что сервис не дает создать задачу для несуществующего пользователя."""
        dto = TaskCreateRawData(user_id=999, text="Задача в никуда")
        
        with pytest.raises(ValueError, match="Пользователь не найден"):
            await task_service_integration.create_task(dto)

    async def test_mark_done_and_list_tasks(self, task_service_integration: TaskService, registered_user: User):
        """Проверяет создание, отметку как выполненной и получение списка задач."""
        assert registered_user.id is not None
        
        dto_1 = TaskCreateRawData(user_id=registered_user.id, text="Завершить отчет")
        dto_2 = TaskCreateRawData(user_id=registered_user.id, text="Позвонить клиенту")
        
        task_1 = await task_service_integration.create_task(dto_1)
        task_2 = await task_service_integration.create_task(dto_2)
        
        assert task_1.id is not None
        updated_task_1 = await task_service_integration.mark_done(task_1.id)
        
        assert updated_task_1.done is True
        assert task_2.done is False
        
        tasks = await task_service_integration.list_user_tasks(registered_user.id)
        
        assert len(tasks) == 2
        done_task = next(t for t in tasks if t.id == task_1.id)
        assert done_task.done is True
        
    async def test_delete_task(self, task_service_integration: TaskService, registered_user: User):
        """Проверяет создание и удаление задачи через сервис."""
        assert registered_user.id is not None
        dto = TaskCreateRawData(user_id=registered_user.id, text="Удалить тестовый файл")
        task_to_delete = await task_service_integration.create_task(dto)
        task_id = task_to_delete.id
        assert task_id is not None

        success = await task_service_integration.delete_task(task_id)
        assert success is True
        
        # Проверяем, что при попытке получить ее, возникнет ошибка
        with pytest.raises(ValueError):
            await task_service_integration.get_task(task_id)

    async def test_operation_on_non_existent_task_raises_error(self, task_service_integration: TaskService):
        """Проверяет, что операции над несуществующей задачей вызывают ошибку."""
        with pytest.raises(ValueError):
            await task_service_integration.delete_task(99999)
            
        with pytest.raises(ValueError):
            await task_service_integration.mark_done(999999)
            
        with pytest.raises(ValueError):
            await task_service_integration.reopen(99999)
