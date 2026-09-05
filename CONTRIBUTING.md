# Contributing

## Branching

- Team members have write access, push feature branches straight to this repo (or work from your own fork, if you prefer)
- `main` is protected: no direct pushes, PR and 1 review required to merge
- Do all work on a feature branch off an up-to-date `main`:

  ```bash
  git checkout main && git pull
  git checkout -b feat/spectrogram-view
  ```

  ```
  <type>/<short-description>
  feat/spectrogram-view
  fix/csv-parse-error
  docs/setup-instructions
  ```

## Pull requests

1. Push your branch and open a PR against `main`.
2. Fill in the PR template
3. Request a review from another team member
4. Merge your approved PR. Delete the branch after merge.

Keep PRs small and focused. Easier to review, faster to merge.

## Commit messages

- Use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/#summary)
- Add a body if "why" isn't obvious from the summary.

## Project structure

The repository holds two projects with their own toolchains:

- `backend/`
  - Python, managed with uv. The pipeline plus the API that exposes it.
- `frontend/`
  - TypeScript/SvelteKit, managed with pnpm. Everything the user sees.

They communicate over the `/api` HTTP and WebSocket surface. The frontend is built as a static single-page app and served by the backend in production. There is no shared code between the two. Response shapes should be mirrored between `backend/src/acoustic_dashboard/api/` and `frontend/src/lib/` (`types.ts`, `services/`).

Backend stages are modular. All connection handling lives in `backend/src/acoustic_dashboard/api/` so pipeline stages/modules are testable in isolation without a server.

### Database

Postgres 16 via SQLAlchemy 2 (async) and Alembic. Migration is run on startup.

- Models are in `backend/src/acoustic_dashboard/db/models.py`, migrations in `db/migrations/versions/`. Change the model, then:

  ```bash
  cd backend
  uv run alembic revision --autogenerate -m "add machines"   # read the generated file!
  uv run alembic upgrade head
  ```

  Autogenerate misses renames (it sees drop + add) and some constraint changes. Always review the script before committing it, and keep `uv run alembic check` clean.
- Every table that belongs to an organisation has a non-null `org_id`** foreign key to `organisations`, and every query on such a table is scoped by it.
- Tests run against a real Postgres (a `<db>_test` database created on demand), not SQLite. Start one with `docker compose up -d db` before `uv run pytest`.

## Dependencies

Both lockfiles are committed. Add a package only when a change needs it, in the same PR.

### Backend (uv)

- [uv](https://docs.astral.sh/uv/) for dependency management:

  ```bash
  cd backend
  uv add pandas          # runtime dependency
  uv add --dev pytest    # dev-only tooling
  ```

- Never hand-edit `pyproject.toml` dependencies or `uv.lock`. Let `uv add` / `uv remove` do it, so the lockfile stays consistent.
- After pulling someone else's changes, run `uv sync` to match the lockfile.
- Run project code with `uv run <command>` rather than activating `.venv`.

### Frontend (pnpm)

- [pnpm](https://pnpm.io/) on Node 22+ (`frontend/.nvmrc`).

  ```bash
  cd frontend
  pnpm add plotly.js     # runtime dependency
  pnpm add -D vitest     # dev-only tooling
  ```

- After pulling someone else's changes, run `pnpm install` to match `pnpm-lock.yaml`.

## Before you open a PR

```bash
docker compose up -d db      # backend tests need Postgres
cd backend  && uv run pytest && uv run ruff check . && uv run ruff format .
cd frontend && pnpm check && pnpm build
```

If you touched the `Dockerfile` or `compose.yaml`, also confirm `docker compose up -d --build` comes up healthy and `/api/health` responds.

## Data

- Datasets live in `data/` and are not committed (see `.gitignore`).
- Document datasource URLs in README.md
