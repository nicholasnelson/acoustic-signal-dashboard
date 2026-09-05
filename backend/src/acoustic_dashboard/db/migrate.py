"""Run Alembic without the CLI, so the app can migrate itself at startup.

These are blocking calls (Alembic drives its own event loop for the async
engine). From async code, run them via ``asyncio.to_thread``.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def alembic_config(database_url: str) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
    # configparser interpolation: a literal % must be doubled
    cfg.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return cfg


def head_revision(database_url: str) -> str | None:
    return ScriptDirectory.from_config(alembic_config(database_url)).get_current_head()


def upgrade(database_url: str, revision: str = "head") -> None:
    command.upgrade(alembic_config(database_url), revision)


def downgrade(database_url: str, revision: str = "base") -> None:
    command.downgrade(alembic_config(database_url), revision)
