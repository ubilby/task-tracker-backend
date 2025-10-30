import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
# Импорт для работы с асинхронным движком SQLAlchemy
from sqlalchemy.ext.asyncio import create_async_engine 

# Импорт для запуска асинхронных функций в синхронном контексте Alembic
# Используем 'run' из модуля 'asyncio'
from asyncio import run as asyncio_run
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# alembic/env.py

# Импортируем вашу модель Base
import os, sys
sys.path.append(os.getcwd()) # Добавляем корневую директорию в путь

from infrastructure.db.models import Base # <--- Ваш импорт Base
# from infrastructure.db.database import engine # <--- Необязательно, если не хотите использовать engine из того файла

# ...
target_metadata = Base.metadata # Убедитесь, что эта строка указывает на metadata вашей Base

# ...

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # 1. Получаем URL
    url = config.get_main_option("sqlalchemy.url")
    
    # 2. 🟢 Проверка и Уточнение Типа (REQUIRED FIX)
    if url is None:
        raise Exception("Database URL not found in alembic.ini")

    # Получаем URL из alembic.ini
    connectable = create_async_engine(
        url,
        future=True,
    )

    async def run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    asyncio_run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
