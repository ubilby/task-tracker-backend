from typing import List
from domain.models.task import Task
from domain.models.user import User
from services.task_service import TaskService
# from services.user_service import UserService


class TaskApp:
    """Application layer для работы с задачами."""

    def __init__(self, task_service: TaskService) -> None:
        self.task_service = task_service

    def create_task(self, user_id: int, text: str) -> Task:
        return self.task_service.create_task(user_id, text)

    def mark_done(self, task_id: int) -> None:
        self.task_service.mark_done(task_id)

    def reopen(self, task_id: int) -> None:
        self.task_service.reopen(task_id)

    def list_tasks(self, user_id: int) -> List[Task]:
        return self.task_service.list_user_tasks(user_id)

    def get_task(self, task_id: int) -> Task | None:
        """Возвращает задачу по ID."""
        return self.task_service.get_task(task_id)