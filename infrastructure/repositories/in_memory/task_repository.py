from typing import List, Optional
from domain.models.task import Task
from domain.models.user import User
from domain.repositories.task_repository import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id = 1

    async def save(self, task: Task) -> Task:
        if (task.id is None):
            task.id = self._next_id
            self._next_id += 1
            self._tasks.append(task)

        else:
            for i, t in enumerate(self._tasks):
                if t.id == task.id:
                    self._tasks[i] = task
                    break

        return task

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        return next((t for t in self._tasks if t.id == task_id), None)

    async def list_by_user(self, user: User) -> List[Task]:
        return [t for t in self._tasks if t.creator.id == user.id]
