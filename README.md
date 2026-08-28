# Acoustic Signal Dashboard

HIT401 Capstone Project (CDU, Semester 2 2026)

A dashboard for exploring and analysing acoustic signal data.

> Work in progress.

The project is split in two: a **Python backend** that runs the capture analysis detection pipeline and serves its output over REST and a WebSocket, and a **TypeScript frontend** that renders it. They talk over `/api` only, so either side can be worked on without blocking the other.

## Getting started

Install [uv](https://docs.astral.sh/uv/) for the backend and [pnpm](https://pnpm.io/) (on Node 22+) for the frontend.

```bash
# 1. Install toolchains
# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

corepack enable            # provides pnpm at the version pinned in frontend/package.json

# 2. Clone
git clone https://github.com/nicholasnelson/acoustic-signal-dashboard.git
cd acoustic-signal-dashboard

# 3. Install dependencies from the lockfiles
cd backend  && uv sync      && cd ..
cd frontend && pnpm install && cd ..
```

### Running it

Two terminals:

```bash
# terminal 1 - API on http://127.0.0.1:8000 (docs at /docs)
cd backend && uv run uvicorn acoustic_dashboard.main:app --reload

# terminal 2 - UI on http://localhost:5173
cd frontend && pnpm dev
```

Vite proxies `/api` (HTTP and WebSocket) through to the backend.

### Checks

```bash
cd backend  && uv run pytest && uv run ruff check .
cd frontend && pnpm test && pnpm typecheck && pnpm lint && pnpm build
```

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

Scaffold only.

## License

[MIT](LICENSE).
