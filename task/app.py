from typing import Any, Dict, List

from task.domain.model import Task
from task.dto import CreateTaskDTO, TaskCreateRawData
from task.service import TaskService


class TaskApp:
    """Application layer для работы с задачами."""

    def __init__(self, task_service: TaskService) -> None:
        self.task_service = task_service

    async def create_task(self, data: TaskCreateRawData) -> Task:
        values: Dict[str, Any] = data.model_dump()
        if values["user_id"] is None:
            values["user_id"] = await self.task_service.get_user_by_telegram_id(values["telegram_id"])

        dto: CreateTaskDTO = CreateTaskDTO(text=values["text"], user_id=values["user_id"])

        return await self.task_service.create_task(dto)

    async def mark_done(self, task_id: int) -> Task:
        return await self.task_service.mark_done(task_id)

    async def reopen(self, task_id: int) -> Task:
        return await self.task_service.reopen(task_id)

    async def list_tasks(self, user_id: int) -> List[Task]:
        return await self.task_service.list_user_tasks(user_id)

    async def get_task(self, task_id: int) -> Task:
        return await self.task_service.get_task(task_id)

    async def delete_task(self, task_id: int) -> bool:
        return await self.task_service.delete_task(task_id)
