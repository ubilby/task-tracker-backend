from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from exceptions import TaskNotFoundError, UserNotFoundError
from task.domain.model import Task, User
from task.domain.repository import TaskRepository
from infrastructure.db.models import DBTask


class SQLAlchemyTaskRepository(TaskRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    def _db_to_domain_task(self, db_task: DBTask) -> Task:
        """Хелпер-транслятор для задачи."""
        if db_task.creator is None:
            # Этого не должно случиться, если ORM правильно загрузил данные
            raise UserNotFoundError("У задачи нет создателя")

        domain_user = User(
            id=db_task.creator.id, telegram_id=db_task.creator.telegram_id
        )

        return Task(
            id=db_task.id, text=db_task.text, done=db_task.done, creator=domain_user
        )

    async def save(self, task: Task) -> Task:
        """Сохраняет или обновляет задачу."""
        if task.id is None:
            db_task = DBTask(text=task.text, done=task.done, user_id=task.creator.id)
            self.session.add(db_task)
            await self.session.flush()
            await self.session.refresh(db_task)
            task.id = db_task.id  # Обновляем доменную модель новым ID

        else:
            # Обновление существующей задачи (изменение текста/статуса)
            db_task = await self.session.get(DBTask, task.id)
            if db_task:
                db_task.text = task.text
                db_task.done = task.done

        # Получаем полную доменную модель, чтобы вернуть актуальный объект
        response = await self.get_by_id(task.id)

        if response:

            return response

        raise TaskNotFoundError

    async def get_by_id(
        self, task_id: int
    ) -> Optional[Task]:  # Изменен тип возврата на Optional
        """Получает задачу по ID."""
        # Загружаем DBTask вместе с создателем
        stmt = (
            select(DBTask)
            .where(DBTask.id == task_id)
            .options(joinedload(DBTask.creator))
        )
        result = await self.session.execute(stmt)
        db_task = result.scalars().first()

        if db_task:

            return self._db_to_domain_task(db_task)

        raise TaskNotFoundError

    async def list_by_user(self, user: User) -> List[Task]:
        """Получает список задач для конкретного пользователя."""
        stmt = (
            select(DBTask)
            .where(DBTask.user_id == user.id)
            .options(
                joinedload(DBTask.creator)
            )  # JOIN для получения данных о создателе
        )

        result = await self.session.execute(stmt)
        db_tasks = result.scalars().all()

        return [self._db_to_domain_task(db_task) for db_task in db_tasks]

    async def delete_task(self, id: int) -> bool:
        """Удаляет задачу по ID."""
        db_task = await self.session.get(DBTask, id)

        if db_task:
            await self.session.delete(db_task)
            await self.session.flush()

            return True

        raise TaskNotFoundError
