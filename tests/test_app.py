import pytest
from typing import Generator, List, Optional
from application.app import TaskTrackerApp
from domain.models.user import User
from domain.models.task import Task


names: List[str] = ["Bob", "Alex", "Kate", "AnotherOne", "test", "Temp", ]


@pytest.fixture
def app() -> Generator[TaskTrackerApp, None, None]:
    yield TaskTrackerApp()


@pytest.mark.asyncio
class TestTaskTrackerApp:
    """Тест-класс, покрывающий основные сценарии работы приложения."""

    async def test_user_registration(self, app: TaskTrackerApp) -> None:
        """Проверяет регистрацию нового пользователя."""
        name: str = names.pop()
        user: User = await app.users.register_user(name)

        assert isinstance(user.id, int)
        assert user.nickname == name

    async def test_create_task(self, app: TaskTrackerApp) -> None:
        """Проверяет создание задачи пользователем."""
        name: str = names.pop()
        user: User = await app.users.register_user(name)
        assert user.id
        task: Task = await app.tasks.create_task(user.id, "помыть посуду")

        assert isinstance(task.id, int)
        assert task.text == "помыть посуду"
        assert task.done is False
        assert task.creator.id == user.id

    async def test_mark_done_and_reopen(self, app: TaskTrackerApp) -> None:
        """Проверяет смену статуса задачи."""
        name: str = names.pop()
        user: User = await app.users.register_user(name)
        assert user.id
        task: Task = await app.tasks.create_task(user.id, "купить хлеб")
        assert task.id
        await app.tasks.mark_done(task.id)
        updated: Optional[Task] = await app.tasks.get_task(task.id)
        assert not (updated is None)
        assert updated.done is True

        await app.tasks.reopen(task.id)
        reopened: Optional[Task] = await app.tasks.get_task(task.id)
        assert reopened
        assert reopened.done is False

    async def test_list_tasks_by_user(self, app: TaskTrackerApp) -> None:
        """Проверяет получение списка задач конкретного пользователя."""
        name1, name2 = names.pop(), names.pop()
        user1: User = await app.users.register_user(name1)
        user2: User = await app.users.register_user(name2)

        assert user1.id is not None
        await app.tasks.create_task(user1.id, "купить хлеб")
        await app.tasks.create_task(user1.id, "пропылесосить")
        assert user2.id is not None
        await app.tasks.create_task(user2.id, "сделать зарядку")

        tasks_user1: List[Task] = await app.tasks.list_tasks(user1.id)
        tasks_user2: List[Task] = await app.tasks.list_tasks(user2.id)

        assert len(tasks_user1) == 2
        assert len(tasks_user2) == 1
        assert all(t.creator.id == user1.id for t in tasks_user1)

    async def test_get_nonexistent_task(self, app: TaskTrackerApp) -> None:
        """Проверяет получение несуществующей задачи."""
        task: Optional[Task] = await app.tasks.get_task(999)
        assert task is None

    async def test_get_nonexistent_user(self, app: TaskTrackerApp) -> None:
        """Проверяет получение несуществующего пользователя."""
        user: Optional[User] = await app.users.get_user(999)
        assert user is None