from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories import TaskRepository, UserRepository
from infrastructure.db.database import get_session
from infrastructure.repositories.sqlalchemy import SQLAlchemyUserRepository, SQLAlchemyTaskRepository
from services.user_service import UserService
from services.task_service import TaskService

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
