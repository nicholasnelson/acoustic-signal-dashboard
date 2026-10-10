"""Serve the built frontend as a single-page app.

The SvelteKit app is built with ``adapter-static`` in SPA mode: one ``index.html``
plus hashed assets under ``_app/``. Any path that is not a real file is answered with
``index.html`` so client-side routing (e.g. ``/machines/m1``) survives a page reload.

Mounted after the API routers. Unknown paths under the API prefixes are still 404s
rather than ``index.html``, so a typo in an API call fails loudly.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from starlette.status import HTTP_404_NOT_FOUND

#: Paths under these prefixes belong to the backend and never fall back to the SPA.
RESERVED_PREFIXES = ("api/", "ws/")


def spa_router(static_dir: Path) -> APIRouter:
    static_dir = static_dir.resolve()
    index = static_dir / "index.html"
    router = APIRouter(include_in_schema=False)

    @router.get("/{path:path}")
    async def serve(path: str) -> FileResponse:
        if path.startswith(RESERVED_PREFIXES):
            raise HTTPException(HTTP_404_NOT_FOUND)
        candidate = (static_dir / path).resolve()
        # Refuse anything that escapes the build directory (``..`` segments etc.).
        if candidate.is_relative_to(static_dir) and candidate.is_file():
            return FileResponse(candidate)
        if index.is_file():
            return FileResponse(index)
        raise HTTPException(HTTP_404_NOT_FOUND)

    return router
