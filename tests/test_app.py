import pytest
import pytest_asyncio
from typing import List
from application.app import TaskTrackerApp, get_app_instance
from domain.models import User,Task
from application.dto.dtos import RegisterUserDTO, TaskCreateRawData

ID: int = 1000000


@pytest_asyncio.fixture(scope="class")
async def app():
    """Создает один экземпляр приложения для всех тестов класса."""
    return await get_app_instance()


@pytest_asyncio.fixture(scope="class")
async def test_user(app: TaskTrackerApp):
    """Создает тестового пользователя."""
    return await app.users.register_user(RegisterUserDTO(telegram_id=ID))


@pytest.mark.asyncio
class TestTaskTrackerApp:
    """Тест-класс, покрывающий основные сценарии работы приложения."""

    async def test_user_registration(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет регистрацию нового пользователя."""
        assert isinstance(test_user.id, int)
        assert test_user.telegram_id == ID

    async def test_create_task(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет создание задачи пользователем."""
        assert test_user.id
        task_data: TaskCreateRawData = TaskCreateRawData(user_id=test_user.id, text="помыть посуду")
        task: Task = await app.tasks.create_task(task_data)

        assert isinstance(task.id, int)
        assert task.text == "помыть посуду"
        assert task.done is False
        assert task.creator.id == test_user.id

    async def test_mark_done_and_reopen(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет смену статуса задачи."""
        assert test_user.id
        task: Task = await app.tasks.create_task(TaskCreateRawData(user_id=test_user.id, text="купить хлеб"))
        assert task.id
        await app.tasks.mark_done(task.id)
        updated: Task = await app.tasks.get_task(task.id)
        assert updated is not None
        assert updated.done is True

        await app.tasks.reopen(task.id)
        reopened: Task = await app.tasks.get_task(task.id)
        assert reopened is not None
        assert reopened.done is False

    async def test_list_tasks_by_user(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет получение списка задач конкретного пользователя."""
        user2: User = await app.users.register_user(RegisterUserDTO(telegram_id=(ID + 1)))
        user1: User = await app.users.register_user(RegisterUserDTO(telegram_id=(ID + 2)))

        assert not (user1.id is None)
        await app.tasks.create_task(TaskCreateRawData(user_id=user1.id, text="купить хлеб"))
        await app.tasks.create_task(TaskCreateRawData(user_id=user1.id, text="пропылесосить"))
        assert not (user2.id is None)
        await app.tasks.create_task(TaskCreateRawData(user_id=user2.id, text="сделать зарядку"))

        tasks_user1: List[Task] = await app.tasks.list_tasks(user1.id)
        tasks_user2: List[Task] = await app.tasks.list_tasks(user2.id)

        assert len(tasks_user1) == 2
        assert len(tasks_user2) == 1
        print(tasks_user1)
        assert all(t.creator.id == user1.id for t in tasks_user1)

    async def test_get_nonexistent_task(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет получение несуществующей задачи."""
        with pytest.raises(ValueError):
            await app.tasks.get_task(999)

    async def test_get_nonexistent_user(self, app: TaskTrackerApp, test_user: User) -> None:
        """Проверяет получение несуществующего пользователя."""
        with pytest.raises(ValueError):
            await app.users.get_user(999)
