# Acoustic Signal Dashboard

HIT401 Capstone Project (CDU, Semester 2 2026)

A dashboard for exploring and analysing acoustic signal data.

> Work in progress.

The project is split in two: a **Python backend** that runs the capture analysis detection pipeline and serves its output over REST and a WebSocket, and a **TypeScript frontend** that renders it. They talk over `/api` only, so either side can be worked on without blocking the other. In production the frontend is built to static files and served by the backend, so the whole system is one container plus Postgres.

## Running it

Prerequisite: [Docker](https://docs.docker.com/get-docker/) with Compose v2. Nothing else.

```bash
git clone https://github.com/nicholasnelson/acoustic-signal-dashboard.git
cd acoustic-signal-dashboard
cp .env.example .env        # defaults work as-is; edit to change ports/passwords
docker compose up -d --wait
```

- UI: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

The first start builds the image (a couple of minutes) and applies database migrations. `up --wait` returns once the API is answering.

### Self-hosting

The same three commands on any machine with Docker are a deployment. Before exposing it beyond localhost, set `POSTGRES_PASSWORD` in `.env`. Database contents live in the `pgdata` Docker volume and survive restarts and rebuilds.

```bash
# Update to the latest code
git pull && docker compose up -d --build --wait

# Back up the database
docker compose exec db pg_dump -U asd asd > backup-$(date +%F).sql

# Restore a backup into an empty database
docker compose exec -T db psql -U asd asd < backup-2026-09-05.sql

# Stop (keeps data) / stop and delete all data
docker compose down
docker compose down -v
```

## Developing

Prerequisites: Docker (for Postgres), [uv](https://docs.astral.sh/uv/) for the backend, [pnpm](https://pnpm.io/) on Node 22+ for the frontend.

```bash
# Toolchains
# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

corepack enable            # provides pnpm at the version pinned in frontend/package.json

# Dependencies from the lockfiles
cd backend  && uv sync      && cd ..
cd frontend && pnpm install && cd ..
```

Then three terminals:

```bash
# terminal 1 - Postgres on localhost:5432
docker compose up db

# terminal 2 - API on http://127.0.0.1:8000 (docs at /docs), migrates on start
cd backend && uv run uvicorn acoustic_dashboard.main:app --reload

# terminal 3 - UI with hot reload on http://localhost:5173
cd frontend && pnpm dev
```

Vite proxies `/api` (HTTP and WebSocket) through to the backend. The backend serves the built UI itself if `frontend/build` exists (after `pnpm build`).

Backend settings are `ASD_*` environment variables (see `backend/.env.example`). Compose settings are in the root `.env.example`.

### Checks

```bash
docker compose up -d db     # backend tests need Postgres
cd backend  && uv run pytest && uv run ruff check .
cd frontend && pnpm check && pnpm build
```

Backend tests use a separate `asd_test` database, created automatically, so they never touch dev data.

### Database migrations

Alembic migrations live in `backend/src/acoustic_dashboard/db/migrations/` and run automatically when the app starts. To add one after changing a model:

```bash
cd backend
uv run alembic revision --autogenerate -m "add machines"
uv run alembic upgrade head
```

Read the generated script before committing it.

### Adding a dependency

```bash
cd backend  && uv add pandas         # runtime
cd backend  && uv add --dev pytest   # dev-only
cd frontend && pnpm add plotly.js    # runtime
cd frontend && pnpm add -D vitest    # dev-only
```

## Data

Datasets live in `data/` and are not committed.

Download datasets locally with:

```bash
python scripts/fetch_mimii.py --type fan --snr 6
```

## How we work

Short version: branch -> PR against `main` -> one teammate reviews -> merge

Full conventions in [CONTRIBUTING.md](CONTRIBUTING.md).

## Status

Deployable scaffold: Docker Compose stack (app + Postgres), SPA frontend served by the backend, migrations on startup. Pipeline, organisations and auth are in progress.

## License

[MIT](LICENSE).
