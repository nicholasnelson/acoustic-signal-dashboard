# Frontend

React + TypeScript single-page app, built with Vite and managed with pnpm. Renders the frontend.

## Setup

```bash
cd frontend
pnpm install
```

## Running

Start the backend first (`cd backend && uv run uvicorn acoustic_dashboard.main:app --reload`), then:

```bash
pnpm dev
```

Open http://localhost:5173


## Checks

```bash
pnpm test
pnpm typecheck
pnpm lint
pnpm format
pnpm build
```

## Status

Scaffold.
