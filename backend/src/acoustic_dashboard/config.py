"""Application settings

Values are read from the environment, optionally via a local ``.env`` file.
ENV vars are prefixed with ``ESD_``
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

settings = Settings()
