import pytest
import pytest_asyncio
from typing import List, Optional
from application.app import TaskTrackerApp, get_app_instance
from domain.models.user import User
from domain.models.task import Task


@pytest_asyncio.fixture(scope="class")
async def app():
    """Создает один экземпляр приложения для всех тестов класса."""
    return await get_app_instance()


@pytest_asyncio.fixture(scope="class")
async def test_user(app: TaskTrackerApp):
    """Создает тестового пользователя."""
    return await app.users.register_user("test_user")


@pytest.mark.asyncio
class TestTaskTrackerApp:
    """Тест-класс, покрывающий основные сценарии работы приложения."""

    async def test_user_registration(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет регистрацию нового пользователя."""
        assert isinstance(test_user.id, int)
        assert test_user.nickname == "test_user"

    async def test_create_task(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет создание задачи пользователем."""
        assert test_user.id
        task: Task = await app.tasks.create_task(test_user.id, "помыть посуду")

        assert isinstance(task.id, int)
        assert task.text == "помыть посуду"
        assert task.done is False
        assert task.creator.id == test_user.id

    async def test_mark_done_and_reopen(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет смену статуса задачи."""
        assert test_user.id
        task: Task = await app.tasks.create_task(test_user.id, "купить хлеб")
        assert task.id
        await app.tasks.mark_done(task.id)
        updated: Optional[Task] = await app.tasks.get_task(task.id)
        assert updated is not None
        assert updated.done is True

        await app.tasks.reopen(task.id)
        reopened: Optional[Task] = await app.tasks.get_task(task.id)
        assert reopened is not None
        assert reopened.done is False

    async def test_list_tasks_by_user(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет получение списка задач конкретного пользователя."""
        user2: User = await app.users.register_user("temp")
        user1: User = await app.users.register_user("test")

        assert user1.id is not None
        await app.tasks.create_task(user1.id, "купить хлеб")
        await app.tasks.create_task(user1.id, "пропылесосить")
        assert user2.id is not None
        await app.tasks.create_task(user2.id, "сделать зарядку")

        tasks_user1: List[Task] = await app.tasks.list_tasks(user1.id)
        tasks_user2: List[Task] = await app.tasks.list_tasks(user2.id)
        
        assert len(tasks_user1) == 2
        assert len(tasks_user2) == 1
        print(tasks_user1)
        assert all(t.creator.id == user1.id for t in tasks_user1)

    async def test_get_nonexistent_task(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет получение несуществующей задачи."""
        task: Optional[Task] = await app.tasks.get_task(999)
        assert task is None

    async def test_get_nonexistent_user(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет получение несуществующего пользователя."""
        user: Optional[User] = await app.users.get_user(999)
        assert user is None