import pytest
import pytest_asyncio
from typing import List, Optional, Tuple

from domain.models import User, Task
from infrastructure.repositories.in_memory import InMemoryUserRepository, InMemoryTaskRepository
from services import UserService, TaskService
from application.dto.dtos import CreateTaskDTO


@pytest_asyncio.fixture
async def services() -> Tuple[UserService, TaskService]:
    """Создаёт in-memory реализации репозиториев и сервисов."""
    user_repo = InMemoryUserRepository()
    task_repo = InMemoryTaskRepository()
    user_service = UserService(user_repo)
    task_service = TaskService(task_repo, user_repo)
    return user_service, task_service


@pytest.mark.asyncio
class TestTaskAndUserServices:
    """Интеграционные тесты для сервисов пользователя и задач."""

    @pytest.mark.asyncio
    async def test_add_user_and_check_nickname(
        self,
        services: Tuple[UserService, TaskService]
    ) -> None:
        """Проверяет регистрацию пользователя и уникальность никнейма."""
        user_service, _ = services

        user: User = await user_service.register_user(telegram_id=1000000)
        assert user.id is not None
        assert user.telegram_id == 1000000

        # повторный никнейм — ошибка
        with pytest.raises(ValueError):
            await user_service.register_user(1000000)

    @pytest.mark.asyncio
    async def test_add_task_and_change_status(
        self,
        services: Tuple[UserService, TaskService]
    ) -> None:
        """Проверяет создание задачи и изменение её статуса."""
        user_service, task_service = services
        user: User = await user_service.register_user(telegram_id=1000000)
        assert user.id is not None
        # создаём задачу
        task: Optional[Task] = await task_service.create_task(CreateTaskDTO(
            user_id=user.id,
            text="Сходить в магазин"
        ))
        assert isinstance(task.id, int)
        assert task.done is False
        assert task.text == "Сходить в магазин"

        # выполняем задачу
        await task_service.mark_done(task.id)
        assert task.id is not None
        task = await task_service.get_task(task.id)
        assert task is not None
        assert task.done is True

        # возвращаем обратно
        assert task.id is not None
        await task_service.reopen(task.id)
        task = await task_service.get_task(task.id)
        assert task is not None
        assert task.done is False

    @pytest.mark.asyncio
    async def test_list_tasks_by_user(
        self,
        services: Tuple[UserService, TaskService]
    ) -> None:
        """Проверяет получение списка задач по пользователю."""
        user_service, task_service = services
        user1: User = await user_service.register_user(telegram_id=1000002)
        user2: User = await user_service.register_user(telegram_id=1000003)

        # создаём задачи
        assert user1.id is not None
        await task_service.create_task(CreateTaskDTO(user_id=user1.id, text="купить хлеб"))
        await task_service.create_task(CreateTaskDTO(user_id=user1.id, text="помыть посуду"))
        assert user2.id is not None
        await task_service.create_task(CreateTaskDTO(user_id=user2.id, text="сделать зарядку"))

        tasks_user1: List[Task] = await task_service.list_user_tasks(user1.id)
        tasks_user2: List[Task] = await task_service.list_user_tasks(user2.id)

        assert len(tasks_user1) == 2
        assert len(tasks_user2) == 1
        assert all(t.creator.id == user1.id for t in tasks_user1)
