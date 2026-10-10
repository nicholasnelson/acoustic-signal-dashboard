"""Shared fixtures.

Database tests run against Postgres. They use a dedicated ``<dbname>_test``
database next to the configured one, created on demand. Point ASD_DATABASE_URL
at ``docker compose up db`` (the default) or any other Postgres.
"""

import asyncio
from collections.abc import Iterator

import asyncpg
import pytest
from sqlalchemy.engine import URL, make_url

from acoustic_dashboard.config import settings
from acoustic_dashboard.db import migrate


async def _ensure_database(url: URL) -> None:
    """Create ``url.database`` if it doesn't exist, via the ``postgres`` maintenance DB."""
    admin = await asyncpg.connect(
        host=url.host,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        database="postgres",
    )
    try:
        exists = await admin.fetchval("select 1 from pg_database where datname = $1", url.database)
        if not exists:
            await admin.execute(f'create database "{url.database}"')
    finally:
        await admin.close()


@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = make_url(settings.database_url)
    url = url.set(database=f"{url.database}_test")
    asyncio.run(_ensure_database(url))
    return url.render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def migrated_db(test_database_url: str) -> Iterator[str]:
    """Test database at the latest migration; torn down to empty afterwards."""
    migrate.upgrade(test_database_url)
    yield test_database_url
    migrate.downgrade(test_database_url)
