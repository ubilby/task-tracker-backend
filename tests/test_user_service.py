import pytest
from typing import List, Optional, Tuple

from domain.models.user import User
from domain.models.task import Task
from infrastructure.repositories.in_memory.user_repository import (
    InMemoryUserRepository
)
from infrastructure.repositories.in_memory.task_repository import (
    InMemoryTaskRepository
)
from services.user_service import UserService
from services.task_service import TaskService


@pytest.fixture
def services() -> Tuple[UserService, TaskService]:
    """Создаёт in-memory реализации репозиториев и сервисов."""
    user_repo = InMemoryUserRepository()
    task_repo = InMemoryTaskRepository()
    user_service = UserService(user_repo)
    task_service = TaskService(task_repo, user_repo)
    return user_service, task_service


class TestTaskAndUserServices:
    """Интеграционные тесты для сервисов пользователя и задач."""

    def test_add_user_and_check_nickname(
        self,
        services: Tuple[UserService, TaskService]
    ) -> None:
        """Проверяет регистрацию пользователя и уникальность никнейма."""
        user_service, _ = services

        user: User = user_service.register_user("alex")
        assert user.id is not None
        assert user.nickname == "alex"

        # повторный никнейм — ошибка
        with pytest.raises(ValueError):
            user_service.register_user("alex")

    def test_add_task_and_change_status(
        self,
        services: Tuple[UserService, TaskService]
    ) -> None:
        """Проверяет создание задачи и изменение её статуса."""
        user_service, task_service = services
        user: User = user_service.register_user("bob")
        assert user.id is not None
        # создаём задачу
        task: Optional[Task] = task_service.create_task(
            user_id=user.id,
            text="Сходить в магазин"
        )
        assert isinstance(task.id, int)
        assert task.done is False
        assert task.text == "Сходить в магазин"

        # выполняем задачу
        task_service.mark_done(task.id)
        assert task.id is not None
        task = task_service.get_task(task.id)
        assert task is not None
        assert task.done is True

        # возвращаем обратно
        assert task.id is not None
        task_service.reopen(task.id)
        task = task_service.get_task(task.id)
        assert task is not None
        assert task.done is False

    def test_list_tasks_by_user(
        self,
        services: Tuple[UserService, TaskService]
    ) -> None:
        """Проверяет получение списка задач по пользователю."""
        user_service, task_service = services
        user1: User = user_service.register_user("alex")
        user2: User = user_service.register_user("bob")

        # создаём задачи
        assert user1.id is not None
        task_service.create_task(user1.id, "купить хлеб")
        task_service.create_task(user1.id, "помыть посуду")
        assert user2.id is not None
        task_service.create_task(user2.id, "сделать зарядку")

        tasks_user1: List[Task] = task_service.list_user_tasks(user1.id)
        tasks_user2: List[Task] = task_service.list_user_tasks(user2.id)

        assert len(tasks_user1) == 2
        assert len(tasks_user2) == 1
        assert all(t.creator.id == user1.id for t in tasks_user1)
