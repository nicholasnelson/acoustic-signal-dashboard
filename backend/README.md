# Backend

FastAPI service for the acoustic signal dashboard. Owns the capture analysis detection pipeline and serves its output to the frontend.

## Setup

```bash
cd backend
uv sync
docker compose -f ../compose.yaml up -d db   # Postgres on localhost:5432
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
  - db/             # SQLAlchemy models, session factories, Alembic migrations
  - config.py       # environment-driven settings, .env supported
  - main.py         # app factory + lifespan (migrates, opens the DB engine)
```
Each stage is its own package so it can be swapped independently. Keep web concerns in `api/`; the stages should not import FastAPI, so each can be tested without a server.

## Configuration

(OPTIONAL) Copy `.env.example` to `.env` and edit as needed. Defaults are in `config.py`.

## Live microphone capture (optional)

The capture stage can use either prerecorded WAV replay or a physical microphone/input while
emitting the same `AudioChunk` contract. Live capture is an optional local-development feature:

```bash
uv sync
uv pip install -r requirements-live.txt
uv run python scripts/live_audio_demo.py --list-devices
uv run python scripts/live_audio_demo.py --stream machine01 --device 0
```

Omit `--device` to use the operating system's default input. By default the source preserves the
input device's native sample rate in `AudioChunk.sample_rate`; resampling to the 16 kHz MIMII rate
belongs in the downstream analysis/pre-processing stage.