"""Alembic environment (async engine).

Reached two ways:
- programmatically from ``acoustic_dashboard.db.migrate`` (app startup, tests),
  which supplies ``sqlalchemy.url``;
- the ``alembic`` CLI via ``backend/alembic.ini``, which doesn't, so we fall
  back to the app settings (``ASD_DATABASE_URL``).
"""

import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from acoustic_dashboard.db import models  # noqa: F401  registers every table on Base
from acoustic_dashboard.db.base import Base

config = context.config
if not config.get_main_option("sqlalchemy.url"):
    from acoustic_dashboard.config import settings

    config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL to stdout instead of executing it (``alembic upgrade --sql``)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
