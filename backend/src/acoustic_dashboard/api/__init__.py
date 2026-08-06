"""HTTP and WebSocket surface of the backend."""

from fastapi import APIRouter

from acoustic_dashboard.api import routes

router = APIRouter()
router.include_router(routes.router)

__all__ = ["router"]
