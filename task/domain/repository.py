from typing import List, Protocol

from task.domain.model import Task, User


class TaskRepository(Protocol):

    async def save(self, task: Task) -> Task:
        ...

    async def get_by_id(self, task_id: int) -> Task:
        ...

    async def list_by_user(self, user: User) -> List[Task]:
        ...

    async def delete_task(self, id: int) -> bool:
        ...
