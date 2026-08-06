"""REST endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from acoustic_dashboard import __version__

router = APIRouter(tags=["system"])


class Health(BaseModel):
    status: str
    version: str


@router.get("/health")
async def health() -> Health:
    """Liveness probe"""
    return Health(
        status="ok",
        version=__version__,
    )
