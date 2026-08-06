"""FastAPI entry point

Run in development with::

    uv run uvicorn acoustic_dashboard.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from acoustic_dashboard import __version__
from acoustic_dashboard.api import router
from acoustic_dashboard.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Acoustic Signal Dashboard API",
        version=__version__,
        summary="Streams analysis windows and alerts for replayed machine recordings",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api")
    return app


app = create_app()
