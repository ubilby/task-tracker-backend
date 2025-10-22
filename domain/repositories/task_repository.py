from typing import Protocol, Optional, List
from domain.models.task import Task
from domain.models.user import User


class TaskRepository(Protocol):

    def save(self, task: Task) -> Task:
        ...

    def get_by_id(self, task_id: int) -> Optional[Task]:
        ...

    def list_by_user(self, user: User) -> List[Task]:
        ...
