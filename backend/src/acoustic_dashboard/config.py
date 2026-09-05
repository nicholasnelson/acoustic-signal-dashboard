"""Application settings

Values are read from the environment, optionally via a local ``.env`` file.
ENV vars are prefixed with ``ASD_``
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/src/acoustic_dashboard/config.py -> repository root
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ASD_", env_file=".env", extra="ignore")

    #: Downloaded datasets
    data_dir: Path = REPO_ROOT / "data"

    cors_origins: list[str] = ["http://localhost:5173"]

    #: Built frontend (``pnpm build`` output). Served as a single-page app when the
    #: directory exists; ignored otherwise, so native dev with ``pnpm dev`` is unaffected.
    static_dir: Path = REPO_ROOT / "frontend" / "build"

    #: SQLAlchemy URL. Postgres with the asyncpg driver; the default matches
    #: ``docker compose up db``. compose.yaml overrides it for the app container.
    database_url: str = "postgresql+asyncpg://asd:asd@localhost:5432/asd"

    #: Apply pending Alembic migrations when the app starts
    run_migrations: bool = True


settings = Settings()
