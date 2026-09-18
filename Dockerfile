# syntax=docker/dockerfile:1
#
# Single app image: the SvelteKit frontend is built to static files in a Node
# stage, then copied into a Python image that runs the FastAPI backend and
# serves those files. No Node at runtime.
#
#   docker build -t acoustic-signal-dashboard .
#   docker run -p 8000:8000 acoustic-signal-dashboard

# FRONTEND
FROM node:22-alpine AS frontend
WORKDIR /src
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
# corepack uses the pnpm version pinned in package.json ("packageManager")
RUN corepack enable
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

# BACKEND
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS backend
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    PYTHONUNBUFFERED=1

# Dependencies first so they cache independently of source change
COPY backend/pyproject.toml backend/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project
COPY backend/ ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

COPY --from=frontend /src/build /app/static

RUN useradd --system --no-create-home app && chown -R app:app /app
USER app

ENV PATH="/app/.venv/bin:$PATH" \
    ASD_STATIC_DIR=/app/static
EXPOSE 8000
CMD ["uvicorn", "acoustic_dashboard.main:app", "--host", "0.0.0.0", "--port", "8000"]
