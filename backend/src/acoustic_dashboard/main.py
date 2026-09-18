"""FastAPI entry point

Run in development with::

    uv run uvicorn acoustic_dashboard.main:app --reload
"""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from acoustic_dashboard import __version__
from acoustic_dashboard.api import router
from acoustic_dashboard.api.static import spa_router
from acoustic_dashboard.config import Settings, settings
from acoustic_dashboard.db import migrate
from acoustic_dashboard.db.session import make_engine, make_sessionmaker

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    config: Settings = app.state.settings
    if config.run_migrations:
        log.info("applying database migrations")
        # Alembic is blocking and runs its own event loop; keep it off ours.
        await asyncio.to_thread(migrate.upgrade, config.database_url)
        log.info("database at revision %s", migrate.head_revision(config.database_url))
    engine = make_engine(config.database_url)
    app.state.engine = engine
    app.state.sessionmaker = make_sessionmaker(engine)
    try:
        yield
    finally:
        await engine.dispose()


def create_app(config: Settings = settings) -> FastAPI:
    # No-op if the host process (pytest, a custom runner) already configured logging.
    # Uvicorn only configures its own loggers, so without this Alembic and our own
    # INFO lines would be dropped in the container.
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s: %(message)s")
    app = FastAPI(
        title="Acoustic Signal Dashboard API",
        version=__version__,
        summary="Streams analysis windows and alerts for replayed machine recordings",
        lifespan=lifespan,
    )
    app.state.settings = config
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api")
    # Production: the built frontend is served from the same origin as the API.
    # Native dev: the directory usually doesn't exist and Vite serves the UI instead.
    if config.static_dir.is_dir():
        app.include_router(spa_router(config.static_dir))
    return app


app = create_app()
