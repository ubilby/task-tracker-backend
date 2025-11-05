from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.database import get_session
from task.sql_repository import SQLAlchemyTaskRepository, TaskRepository
from user.sql_repository import SQLAlchemyUserRepository, UserRepository
from .app import UserService, UserApp
from .app import TaskService, TaskApp

# 1. Зависимость для UserRepository (скрывает сложность SQLAlchemy)
def get_user_repo(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return SQLAlchemyUserRepository(session)


# 2. Зависимость для TaskRepository
def get_task_repo(session: AsyncSession = Depends(get_session)) -> TaskRepository:
    return SQLAlchemyTaskRepository(session)


# 3. Зависимость для UserService (внедряет репозиторий, используя Протокол)
def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)


# 4. Зависимость для TaskService (внедряет оба репозитория)
def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repo),
    user_repo: UserRepository = Depends(get_user_repo)
) -> TaskService:
    return TaskService(task_repo, user_repo)

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

