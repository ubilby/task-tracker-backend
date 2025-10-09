import pytest

from domain.models.user import User
from infrastructure.repositories.in_memory.user_repository import InMemoryUserRepository
from infrastructure.repositories.in_memory.task_repository import InMemoryTaskRepository
from services.user_service import UserService
from services.task_service import TaskService


@pytest.fixture
def setup_services():
    user_repo = InMemoryUserRepository()
    task_repo = InMemoryTaskRepository()
    user_service = UserService(user_repo)
    task_service = TaskService(task_repo, user_repo)
    return user_service, task_service


def test_add_user_and_check_nickname(setup_services):
    user_service, _ = setup_services

    user = user_service.register_user("alex")
    assert user.id is not None
    assert user.nickname == "alex"

    # проверяем, что никнейм не может повторяться
    with pytest.raises(ValueError):
        user_service.register_user("alex")


def test_add_task_and_change_status(setup_services):
    user_service, task_service = setup_services
    user = user_service.register_user("bob")

    # создаём задачу
    task = task_service.create_task(user_id=user.id, text="Сходить в магазин")

    assert task.id is not None
    assert not task.done
    assert task.text == "Сходить в магазин"

    # меняем статус
    task_service.mark_done(task.id)
    task = task_service.get_task(task.id)
    assert task.done

    # возвращаем в невыполненные
    task_service.reopen(task.id)
    task = task_service.get_task(task.id)
    assert not task.done


def test_list_tasks_by_user(setup_services):
    user_service, task_service = setup_services
    user1 = user_service.register_user("alex")
    user2 = user_service.register_user("bob")

    # создаём задачи
    task_service.create_task(user1.id, "купить хлеб")
    task_service.create_task(user1.id, "помыть посуду")
    task_service.create_task(user2.id, "сделать зарядку")

    tasks_user1 = task_service.list_user_tasks(user1.id)
    tasks_user2 = task_service.list_user_tasks(user2.id)

    assert len(tasks_user1) == 2
    assert len(tasks_user2) == 1
    assert all(t.creator.id == user1.id for t in tasks_user1)
