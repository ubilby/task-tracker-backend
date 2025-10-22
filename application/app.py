from typing import Optional
from domain.repositories import UserRepository, TaskRepository
from infrastructure.repositories.in_memory.user_repository import InMemoryUserRepository
from infrastructure.repositories.in_memory.task_repository import InMemoryTaskRepository
from services.user_service import UserService
from services.task_service import TaskService
from application.user_app import UserApp
from application.task_app import TaskApp


class TaskTrackerApp:
    """Фасад верхнего уровня, объединяющий все части приложения."""

    def __init__(self, user_repo: Optional[UserRepository] = None, task_repo: Optional[TaskRepository] = None) -> None:
        user_repo = InMemoryUserRepository() if user_repo is None else user_repo
        task_repo = InMemoryTaskRepository() if task_repo is None else task_repo

        user_service = UserService(user_repo)
        task_service = TaskService(task_repo, user_repo)

        self.users = UserApp(user_service)
        self.tasks = TaskApp(task_service)


def get_app_instance() -> TaskTrackerApp:

    return TaskTrackerApp()
