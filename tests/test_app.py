import pytest
from typing import Generator, List, Optional
from application.app import TaskTrackerApp
from domain.models.user import User
from domain.models.task import Task
from infrastructure.repositories.in_memory.task_repository import (
    InMemoryTaskRepository
)
from infrastructure.repositories.in_memory.user_repository import (
    InMemoryUserRepository
)


@pytest.fixture
def app() -> Generator[TaskTrackerApp, None, None]:
    # тест InMemoryStaff
    user_repo = InMemoryUserRepository()
    task_repo = InMemoryTaskRepository()
    yield TaskTrackerApp(user_repo=user_repo, task_repo=task_repo)


class TestTaskTrackerApp:
    """Тест-класс, покрывающий основные сценарии работы приложения."""

    def test_user_registration(self, app: TaskTrackerApp) -> None:
        """Проверяет регистрацию нового пользователя."""
        user: User = app.users.register_user("alex")

        assert isinstance(user.id, int)
        assert user.nickname == "alex"

    def test_create_task(self, app: TaskTrackerApp) -> None:
        """Проверяет создание задачи пользователем."""
        user: User = app.users.register_user("bob")
        assert user.id
        task: Task = app.tasks.create_task(user.id, "помыть посуду")

        assert isinstance(task.id, int)
        assert task.text == "помыть посуду"
        assert task.done is False
        assert task.creator.id == user.id

    def test_mark_done_and_reopen(self, app: TaskTrackerApp) -> None:
        """Проверяет смену статуса задачи."""
        user: User = app.users.register_user("kate")
        assert user.id
        task: Task = app.tasks.create_task(user.id, "купить хлеб")
        assert task.id
        app.tasks.mark_done(task.id)
        updated: Optional[Task] = app.tasks.get_task(task.id)
        assert not (updated is None)
        assert updated.done is True

        app.tasks.reopen(task.id)
        reopened: Optional[Task] = app.tasks.get_task(task.id)
        assert reopened
        assert reopened.done is False

    def test_list_tasks_by_user(self, app: TaskTrackerApp) -> None:
        """Проверяет получение списка задач конкретного пользователя."""
        user1: User = app.users.register_user("alex")
        user2: User = app.users.register_user("bob")

        assert user1.id is not None
        app.tasks.create_task(user1.id, "купить хлеб")
        app.tasks.create_task(user1.id, "пропылесосить")
        assert user2.id is not None
        app.tasks.create_task(user2.id, "сделать зарядку")

        tasks_user1: List[Task] = app.tasks.list_tasks(user1.id)
        tasks_user2: List[Task] = app.tasks.list_tasks(user2.id)

        assert len(tasks_user1) == 2
        assert len(tasks_user2) == 1
        assert all(t.creator.id == user1.id for t in tasks_user1)
