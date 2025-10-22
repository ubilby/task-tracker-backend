import pytest
import uuid
from fastapi.testclient import TestClient
from api.fastAPI_app import app
from api.schemas.task import TaskCreateRequest, TaskUpdateStatusRequest
from dotenv import load_dotenv
from os import getenv

load_dotenv()

client = TestClient(app)
SUPERUSER_HEADERS = {"Authorization": f"Bearer {getenv('BOT_TOKEN')}"}


@pytest.fixture
def create_user():
    """Создаёт тестового пользователя и возвращает его JSON."""
    nickname = f"TestUser_{uuid.uuid4().hex[:8]}"
    payload = {"nickname": nickname}
    response = client.post("/user/", json=payload, headers=SUPERUSER_HEADERS)
    assert response.status_code == 200, response.text
    return response.json()


def test_create_user():
    name = "Alice"
    payload = {"nickname": name}
    response = client.post("/user/", json=payload, headers=SUPERUSER_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == name


def test_cannot_register_duplicate_user():
    payload = {"nickname": "Bob"}
    response1 = client.post("/user/", json=payload, headers=SUPERUSER_HEADERS)
    assert response1.status_code == 200

    response2 = client.post("/user/", json=payload, headers=SUPERUSER_HEADERS)
    assert response2.status_code == 400
    assert "nickname уже занят" in response2.json()["detail"].lower()


def test_create_task_for_user(create_user):
    user = create_user
    task_data = TaskCreateRequest(user_id=user["id"], text="Buy milk")
    response = client.post("/task/", json=task_data.model_dump(), headers=SUPERUSER_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Buy milk"
    assert data["done"] is False


def test_get_task(create_user):
    user = create_user
    task_data = TaskCreateRequest(user_id=user["id"], text="Buy bread")
    create_resp = client.post("/task/", json=task_data.model_dump(), headers=SUPERUSER_HEADERS)
    task = create_resp.json()

    response = client.get(f"/task/{task['id']}", headers=SUPERUSER_HEADERS)
    print(f"test_get_task() reponse: {response}")
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Buy bread"


def test_update_task_status(create_user):
    user = create_user
    task_data = TaskCreateRequest(user_id=user["id"], text="Buy butter")
    create_resp = client.post("/task/", json=task_data.model_dump(), headers=SUPERUSER_HEADERS)
    task = create_resp.json()

    status_data = TaskUpdateStatusRequest(done=True)
    response = client.patch(f"/task/{task['id']}", json=status_data.model_dump(), headers=SUPERUSER_HEADERS)
    print(f"test_get_task() reponse: {response}")

    assert response.status_code == 200
    data = response.json()
    assert data["done"] is True


def test_get_tasks_for_user(create_user):
    user = create_user
    client.post("/task/", json={"text": "Task 1", "user_id": user["id"]}, headers=SUPERUSER_HEADERS)
    client.post("/task/", json={"text": "Task 2", "user_id": user["id"]}, headers=SUPERUSER_HEADERS)

    response = client.get("/task/", params={"user_id": user["id"]}, headers=SUPERUSER_HEADERS)
    assert response.status_code == 200
    data = response.json()
    titles = [t["text"] for t in data]
    assert "Task 1" in titles
    assert "Task 2" in titles
    assert len(data) == 2
