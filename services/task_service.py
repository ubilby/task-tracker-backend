from typing import List

from domain.models import Task, User
from domain.repositories.task_repository import TaskRepository
from domain.repositories.user_repository import UserRepository
from application.dto.dtos import CreateTaskDTO


class TaskService:
    def __init__(self, task_repo: TaskRepository, user_repo: UserRepository):
        self.task_repo = task_repo
        self.user_repo = user_repo

    async def create_task(self, data: CreateTaskDTO) -> Task:
        user_id: int = data.user_id
        user: User = await self.user_repo.get_user(user_id)
        task = Task(id=None, text=data.text, creator=user)

        return await self.task_repo.save(task)

    async def mark_done(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        task.mark_done()
        await self.task_repo.save(task)

        return task

    async def reopen(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        if not task:
            raise ValueError("Задача не найдена")

        task.reopen()
        await self.task_repo.save(task)

        return task

    async def list_user_tasks(self, user_id: int) -> List[Task]:
        user = await self.user_repo.get_user(user_id)

        if not user:
            raise ValueError("Пользователь не найден")

        return await self.task_repo.list_by_user(user)

    async def get_task(self, task_id: int) -> Task:
        return await self.task_repo.get_by_id(task_id)

    async def delete_task(self, id: int) -> bool:
        return await self.task_repo.delete_task(id)

    async def get_user_by_telegram_id(self, telegram_id: int) -> int:
        return await self.user_repo.get_user_by_telegram_id(telegram_id)
