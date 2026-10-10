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

## Running the pipeline

The backend pulls audio from network devices: each source in the sources config has a WebSocket `url`. The device server stands in for networked microphones. It serves each machine in `machine_config.example.json` at `ws://127.0.0.1:9001/<machine>`, replaying a looping WAV playlist (or a live mic, see below).

```bash
uv run python -m acoustic_dashboard.capture.device_server machine_config.example.json
```

Then start the API with a runner for each source in `sources.example.json` (`ASD_RUN_MIGRATIONS=false` if Postgres isn't running). Events stream on `WS /api/stream`:

```bash
ASD_SOURCES_CONFIG=sources.example.json uv run uvicorn acoustic_dashboard.main:app
```

The runner calibrates live: the first `calibration_windows` windows are assumed normal.

## Live microphone capture (optional)

The capture stage can use either prerecorded WAV replay or a physical microphone/input while
emitting the same `AudioChunk` contract. Live capture is an optional local-development feature:

```bash
uv sync --extra live
uv run python scripts/live_audio_demo.py --list-devices
uv run python scripts/live_audio_demo.py --stream machine01 --device 0
```

To serve a mic from the device server, give a machine `"mic": <device index or null for the default input>` instead of a `"playlist"`. One capture is shared by every connected client.

Omit `--device` to use the operating system's default input. By default the source preserves the
input device's native sample rate in `AudioChunk.sample_rate`; resampling to the 16 kHz MIMII rate
belongs in the downstream analysis/pre-processing stage.