from os import getenv, path
from sys import path as syspath

syspath.insert(0, path.abspath(path.join(path.dirname(__file__), "..")))

from typing import AsyncGenerator

from dotenv import load_dotenv
import httpx
from httpx import ASGITransport
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from application.dependencies import get_app_instance, TaskTrackerApp
from infrastructure.db.database import engine
from user.sql_repository import SQLAlchemyUserRepository
from task.sql_repository import SQLAlchemyTaskRepository
from user.service import UserService
from task.service import TaskService

load_dotenv()

TEST_BOT_TOKEN = getenv("BOT_TOKEN")

# --- 2. Фикстуры для тестовой среды ---


@pytest.fixture(scope="module")
def bot_auth_header():
    """Возвращает заголовок авторизации, имитирующий бота."""
    return {"Authorization": f"Bearer {TEST_BOT_TOKEN}"}


@pytest.fixture
def override_dependencies(db_session: AsyncSession):
    """
    Фикстура для создания реальной, но изолированной, TaskTrackerApp,
    подключенной к тестовой сессии.
    """
    # 1. Создаем реальные репозитории, использующие тестовую сессию
    user_repo = SQLAlchemyUserRepository(db_session)
    task_repo = SQLAlchemyTaskRepository(db_session)

    # 2. Создаем реальные сервисы, использующие эти репозитории
    user_service = UserService(user_repo)
    task_service = TaskService(task_repo, user_repo)

    # 3. Создаем экземпляр TaskTrackerApp
    tracker_app = TaskTrackerApp(user_service=user_service, task_service=task_service)

    # Функция, которая будет подменять get_app_instance
    def override():
        return tracker_app

    # Переопределяем зависимость на время выполнения теста
    app.dependency_overrides[get_app_instance] = override

    # В роутерах используется getenv("BOT_TOKEN"),
    # для корректной работы сравнения токенов в тестах
    # import os
    # os.environ["BOT_TOKEN"] = TEST_BOT_TOKEN

    yield

    # Восстанавливаем оригинальную зависимость после теста
    app.dependency_overrides.clear()
    # del os.environ["BOT_TOKEN"]


@pytest_asyncio.fixture
async def client(override_dependencies) -> AsyncGenerator[httpx.AsyncClient, None]:
    """AsyncClient для выполнения запросов к FastAPI."""
    # ИСПРАВЛЕНИЕ: Используем ASGITransport для передачи ASGI-приложения (app) в AsyncClient
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def registered_user_data(
    client: httpx.AsyncClient, bot_auth_header: dict
) -> dict:
    """Создает тестового пользователя и возвращает его данные."""
    response = await client.post(
        "/user/", json={"telegram_id": 99999}, headers=bot_auth_header
    )
    assert response.status_code == 200
    print(f"fixture registered_user_data: {response.json()}")
    return response.json()


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
            await connection.rollback()  # <-- Явный rollback корневой транзакции

            # 6. Закрываем сессию
            await async_session.close()


# --- 3. Тесты API для Роутера Пользователей ---


@pytest.mark.asyncio
class TestUserRouter:

    async def test_post_user_success(
        self, client: httpx.AsyncClient, bot_auth_header: dict
    ):
        """Проверка успешного создания нового пользователя."""
        response = await client.post(
            "/user/", json={"telegram_id": 1001}, headers=bot_auth_header
        )

        assert response.status_code == 200
        data = response.json()
        assert data["telegram_id"] == 1001
        assert "id" in data

    async def test_post_user_duplicate_raises_400(
        self,
        client: httpx.AsyncClient,
        bot_auth_header: dict,
        registered_user_data: dict,
    ):
        """Проверка обработки дубликата: сервис выбрасывает ValueError, API возвращает 400."""
        duplicate_id = registered_user_data["telegram_id"]

        response = await client.post(
            "/user/", json={"telegram_id": duplicate_id}, headers=bot_auth_header
        )

        assert response.status_code == 400
        assert "уже зарегестрирован" in response.json()["detail"]

    async def test_delete_user_success(
        self,
        client: httpx.AsyncClient,
        bot_auth_header: dict,
        registered_user_data: dict,
    ):
        """Проверка успешного удаления пользователя."""
        user_id = registered_user_data["id"]

        response = await client.delete(f"/user/{user_id}", headers=bot_auth_header)

        assert response.status_code == 200
        assert response.json() == {"success": True}

        # Проверяем, что пользователь действительно удален (проверяем через попытку повторного удаления)
        response = await client.delete(f"/user/{user_id}", headers=bot_auth_header)
        assert response.status_code == 200
        assert response.json() == {"success": False}


# --- 4. Тесты API для Роутера Задач ---


@pytest.mark.asyncio
class TestTaskRouter:

    async def test_post_task_success(
        self,
        client: httpx.AsyncClient,
        bot_auth_header: dict,
        registered_user_data: dict,
    ):
        """Проверка успешного создания задачи."""
        telegram_id = registered_user_data["telegram_id"]

        response = await client.post(
            "/task/",
            json={"telegram_id": telegram_id, "text": "Новая тестовая задача"},
            headers=bot_auth_header,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["text"] == "Новая тестовая задача"
        assert data["done"] is False
        assert data["creator"]["id"] == registered_user_data["id"]

    async def test_post_task_missing_user_id_raises_400(
        self, client: httpx.AsyncClient, bot_auth_header: dict
    ):
        """Проверка, что запрос без user_id возвращает 400."""
        response = await client.post(
            "/task/", json={"text": "Задача без пользователя"}, headers=bot_auth_header
        )
        print(f"response.json()[detail]: {response.json()["detail"]}")
        assert response.status_code == 422
        assert (
            "Value error, Either user_id or telegram_id must be provided"
            in response.json()["detail"][0]["msg"]
        )

    async def test_post_task_non_existent_user_raises_400(
        self, client: httpx.AsyncClient, bot_auth_header: dict
    ):
        """Проверка, что создание задачи для несуществующего пользователя возвращает 400."""
        response = await client.post(
            "/task/",
            json={"telegram_id": 999999, "text": "Задача для несуществующего"},
            headers=bot_auth_header,
        )
        assert response.status_code == 404
        print(f'response.json()["detail"]s {response.json()["detail"]}')
        assert "Пользователь по telegram_id не найден" in response.json()["detail"]

    @pytest_asyncio.fixture
    async def created_task(
        self,
        client: httpx.AsyncClient,
        bot_auth_header: dict,
        registered_user_data: dict,
    ) -> dict:
        """Создает и возвращает тестовую задачу."""
        response = await client.post(
            "/task/",
            json={
                "telegram_id": registered_user_data["telegram_id"],
                "text": "Задача для изменения",
            },
            headers=bot_auth_header,
        )
        return response.json()

    async def test_get_task_success(
        self, client: httpx.AsyncClient, bot_auth_header: dict, created_task: dict
    ):
        """Проверка получения задачи по ID."""
        task_id = created_task["id"]
        response = await client.get(f"/task/{task_id}", headers=bot_auth_header)
        assert response.status_code == 200
        assert response.json()["id"] == task_id
        assert response.json()["done"] is False

    async def test_get_task_not_found_raises_400(
        self, client: httpx.AsyncClient, bot_auth_header: dict
    ):
        """Проверка получения несуществующей задачи возвращает 400 (через ValueError)."""
        response = await client.get("/task/999999", headers=bot_auth_header)
        assert response.status_code == 404

    async def test_list_tasks_success(
        self,
        client: httpx.AsyncClient,
        bot_auth_header: dict,
        registered_user_data: dict,
        created_task: dict,
    ):
        """Проверка получения списка задач пользователя."""
        user_id = registered_user_data["id"]

        response = await client.get(
            f"/task/?user_id={user_id}", headers=bot_auth_header
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        assert tasks[0]["creator"]["id"] == user_id

    async def test_patch_task_mark_done_success(
        self, client: httpx.AsyncClient, bot_auth_header: dict, created_task: dict
    ):
        """Проверка успешной отметки задачи как выполненной."""
        task_id = created_task["id"]

        response = await client.patch(
            f"/task/{task_id}", json={"done": True}, headers=bot_auth_header
        )

        assert response.status_code == 200
        assert response.json()["done"] is True

        # Проверка, что статус сохранился
        check_response = await client.get(f"/task/{task_id}", headers=bot_auth_header)
        assert check_response.json()["done"] is True

    async def test_patch_task_reopen_success(
        self, client: httpx.AsyncClient, bot_auth_header: dict, created_task: dict
    ):
        """Проверка успешного 'переоткрытия' задачи."""
        task_id = created_task["id"]

        # Сначала делаем выполненной
        await client.patch(
            f"/task/{task_id}", json={"done": True}, headers=bot_auth_header
        )

        # Теперь 'переоткрываем'
        response = await client.patch(
            f"/task/{task_id}", json={"done": False}, headers=bot_auth_header
        )

        assert response.status_code == 200
        assert response.json()["done"] is False

    async def test_delete_task_success(
        self, client: httpx.AsyncClient, bot_auth_header: dict, created_task: dict
    ):
        """Проверка успешного удаления задачи."""
        task_id = created_task["id"]

        response = await client.delete(f"/task/{task_id}", headers=bot_auth_header)

        assert response.status_code == 200
        assert response.json() == {"success": True}

        # Проверяем, что задача не найдена после удаления
        response = await client.get(f"/task/{task_id}", headers=bot_auth_header)
        assert response.status_code == 404
