from os import getenv
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DB_TYPE = getenv("DB_TYPE", "sqlite")  # "sqlite" или "postgres"

SQLITE_DB_URL = "sqlite+aiosqlite:///./task_tracker.db"

POSTGRES_DB_URL = "postgresql+asyncpg://admin:admin@localhost:5432/task_db"

if DB_TYPE == "postgres":
    DATABASE_URL = POSTGRES_DB_URL
else:
    DATABASE_URL = SQLITE_DB_URL

# 1. Создаем асинхронный "движок"
engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True для логгирования SQL

# 2. Создаем "фабрику" сессий
# expire_on_commit=False важно для асинхронного кода
AsyncSessionFactory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


# 4. Зависимость (dependency) для FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость, которая предоставляет сессию для каждого запроса.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
