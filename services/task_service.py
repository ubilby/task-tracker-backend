from typing import List, Optional

from domain.models.task import Task
from domain.models.user import User
from domain.repositories.task_repository import TaskRepository
from domain.repositories.user_repository import UserRepository



class TaskService:
    def __init__(self, task_repo: TaskRepository, user_repo: UserRepository):
        self.task_repo = task_repo
        self.user_repo = user_repo

    def create_task(self, user_id: int, text: str) -> Task:
        user = self.user_repo.get_user(user_id)

        if not user:
            raise ValueError("Пользователь не найден")

        task = Task(id=None, text=text, creator=user)

        return self.task_repo.save(task)

    def mark_done(self, task_id: int) -> Task:
        task = self.task_repo.get_by_id(task_id)

        if not task:
            raise ValueError("Задача не найдена")

        task.mark_done()
        self.task_repo.save(task)
        return task

    def reopen(self, task_id: int) -> Task:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Задача не найдена")

        task.reopen()
        self.task_repo.save(task)

        return task

    def list_user_tasks(self, user_id: int) -> List[Task]:
        user = self.user_repo.get_user(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        return self.task_repo.list_by_user(user)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        return self.task_repo.get_by_id(task_id)