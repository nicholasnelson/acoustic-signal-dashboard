"""HTTP and WebSocket surface of the backend."""

from fastapi import APIRouter

from acoustic_dashboard.api import routes, stream

router = APIRouter()
router.include_router(routes.router)
router.include_router(stream.router)

__all__ = ["router"]
