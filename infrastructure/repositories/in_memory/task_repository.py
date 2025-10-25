from typing import List, Optional
from domain.models.task import Task
from domain.models.user import User
from domain.repositories.task_repository import TaskRepository

tasks: List[Task] = []
next_id: List[int] = [0]

class InMemoryTaskRepository(TaskRepository):
    def __init__(self):
        self._tasks: List[Task] = []
        self._next_id = 1

    async def save(self, task: Task) -> Task:
        if (task.id is None):
            task.id = next_id[0]
            next_id[0] += 1
            tasks.append(task)

        else:
            for i, t in enumerate(tasks):
                if t.id == task.id:
                    tasks[i] = task
                    break

        return task

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        return next((t for t in tasks if t.id == task_id), None)

    async def list_by_user(self, user: User) -> List[Task]:
        return [t for t in tasks if t.creator.id == user.id]

    async def delete_task(self, id: int) -> bool:
        index = -1

        for i, task in enumerate(tasks):
            if task.id == id:
                index = i
                break

        if index != -1:
            tasks.pop(index)

            return True

        return False