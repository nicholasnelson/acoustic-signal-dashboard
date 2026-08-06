# Backend

FastAPI service for the acoustic signal dashboard. Owns the capture analysis detection pipeline and serves its output to the frontend.

## Setup

```bash
cd backend
uv sync
```

## Running

```bash
uv run uvicorn acoustic_dashboard.main:app --reload --port 8000
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health

## Checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

## Layout

```
- src/acoustic_dashboard/
  - api/            # REST routes + WebSocket (the only web-facing layer)
  - capture/        # stage 1: playback / mixer / live source
  - analysis/       # stage 2: waveform, spectrogram, band energy
  - detection/      # stage 3: scoring and explainable alerts
  - config.py       # environment-driven settings, .env supported
  - main.py         # app factory
```
Each stage is its own package so it can be swapped independently. Keep web concerns in `api/`; the stages should not import FastAPI, so each can be tested without a server.

## Configuration

(OPTIONAL) Copy `.env.example` to `.env` and edit as needed. Defaults are in `config.py`.