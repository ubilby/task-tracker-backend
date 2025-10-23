import pytest
# import pytest_asyncio
import uuid
from fastapi.testclient import TestClient
from api.fastAPI_app import app, get_app_instance
from application.app import TaskTrackerApp
from api.schemas.task import TaskCreateRequest, TaskUpdateStatusRequest
from dotenv import load_dotenv
from os import getenv

load_dotenv()

SUPERUSER_HEADERS = {"Authorization": f"Bearer {getenv('BOT_TOKEN')}"}


@pytest.fixture
def client() -> TestClient:  # type: ignore
    """
    Главная фикстура!
    Она создает ОДИН экземпляр TaskTrackerApp и "подменяет"
    зависимость get_app_instance на время выполнения ОДНОГО теста.
    """
    # 1. Создаем единственный экземпляр для теста
    shared_app_instance = TaskTrackerApp()

    # 2. Создаем функцию-заменитель
    def override_get_app_instance():
        return shared_app_instance

    # 3. Применяем подмену
    app.dependency_overrides[get_app_instance] = override_get_app_instance

    # 4. Создаем и отдаем клиент
    _client = TestClient(app)
    yield _client  # type: ignore

    # 5. Очищаем подмену после теста (ВАЖНО)
    app.dependency_overrides.clear()


@pytest.fixture
def create_user(client: TestClient):
    """
    Эта фикстура теперь зависит от `client`, который
    гарантированно использует `shared_app_instance`.
    """
    nickname = f"TestUser_{uuid.uuid4().hex[:8]}"
    payload = {"nickname": nickname}
    response = client.post("/user/", json=payload, headers=SUPERUSER_HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def test_create_user(client: TestClient):
    name = "Alice"
    payload = {"nickname": name}
    response = client.post("/user/", json=payload, headers=SUPERUSER_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == name


def test_cannot_register_duplicate_user(client: TestClient):
    payload = {"nickname": "Bob"}
    # Запрос 1 (в shared_app_instance)
    response1 = client.post("/user/", json=payload, headers=SUPERUSER_HEADERS)
    assert response1.status_code == 200

    # Запрос 2 (в тот же самый shared_app_instance)
    response2 = client.post("/user/", json=payload, headers=SUPERUSER_HEADERS)
    assert response2.status_code == 400
    assert "nickname уже занят" in response2.json()["detail"].lower()


def test_create_task_for_user(client: TestClient, create_user):
    user = create_user
    task_data = TaskCreateRequest(user_id=user["id"], text="Buy milk")
    response = client.post(
        "/task/",
        json=task_data.model_dump(),
        headers=SUPERUSER_HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Buy milk"
    assert data["done"] is False


def test_get_task(client: TestClient, create_user):
    user = create_user
    task_data = TaskCreateRequest(user_id=user["id"], text="Buy bread")
    create_resp = client.post(
        "/task/",
        json=task_data.model_dump(),
        headers=SUPERUSER_HEADERS
    )
    task = create_resp.json()

    response = client.get(f"/task/{task['id']}", headers=SUPERUSER_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Buy bread"


def test_update_task_status(client: TestClient, create_user):
    user = create_user
    task_data = TaskCreateRequest(user_id=user["id"], text="Buy butter")
    create_resp = client.post(
        "/task/",
        json=task_data.model_dump(),
        headers=SUPERUSER_HEADERS
    )
    task = create_resp.json()

    status_data = TaskUpdateStatusRequest(done=True)
    response = client.patch(
        f"/task/{task['id']}",
        json=status_data.model_dump(),
        headers=SUPERUSER_HEADERS
    )

    assert response.status_code == 200
    data = response.json()
    assert data["done"] is True


def test_get_tasks_for_user(client: TestClient, create_user):
    user = create_user
    client.post(
        "/task/",
        json={"text": "Task 1", "user_id": user["id"]},
        headers=SUPERUSER_HEADERS
    )
    client.post(
        "/task/",
        json={"text": "Task 2", "user_id": user["id"]},
        headers=SUPERUSER_HEADERS
    )

    response = client.get(
        "/task/",
        params={"user_id": user["id"]},
        headers=SUPERUSER_HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    titles = [t["text"] for t in data]
    assert "Task 1" in titles
    assert "Task 2" in titles
    assert len(data) == 2
