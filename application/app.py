from fastapi import Depends

from user.app import UserService, UserApp
from task.app import TaskService, TaskApp
from .dependencies import get_task_service, get_user_service


class TaskTrackerApp:
    """Фасад верхнего уровня, объединяющий все части приложения."""

    def __init__(
        self,
        user_service: UserService, 
        task_service: TaskService
    ):
        self.users = UserApp(user_service)
        self.tasks = TaskApp(task_service)


async def get_app_instance(
    user_service: UserService = Depends(get_user_service),
    task_service: TaskService = Depends(get_task_service)
) -> TaskTrackerApp:

    return TaskTrackerApp(user_service=user_service, task_service=task_service)
