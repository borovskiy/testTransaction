import asyncio
import os
import sys

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# --- путь к проекту, чтобы видеть пакет app ---
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
from app.models import Base
import app.models  # важно импортировать, чтобы модели были зарегистрированы
# это объект конфигурации Alembic, предоставляет доступ к .ini-файлу
config = context.config
db_url = os.environ.get("DATABASE_URL")
# подставляем URL БД из твоего config.py
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# metadata твоих моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


run_migrations()
