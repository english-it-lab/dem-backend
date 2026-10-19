# AGENTS.md

## Repo layout

| Path | Language | Package manager | Description |
|------|----------|-----------------|-------------|
| `/` (repo root) | Python 3.12 | uv | FastAPI API + PostgreSQL (the deployable) |
| `docs/` | — | — | Technical specification and charters |


## Backend — commands (all require `uv run` prefix)

```bash
uv sync                                  # install deps into .venv
uv run uvicorn app.main:app --reload     # dev server on :8000
uv run alembic upgrade head              # apply migrations (DB must be running)
uv run alembic revision -m "..." --autogenerate  # create new migration
uv run pytest                            # run all tests (mock-based, no DB needed)
uv run ruff check --fix                  # lint
uv run ruff format                       # format
docker compose up db -d                  # database only (default dev mode)
docker compose up --build                # full stack (API + PG 16)
```

## Backend — layered architecture (do NOT break)

```
adapter (FastAPI routers) -> service (business logic) -> repository (SQLAlchemy)
```

Routers import services, never repositories. Schemas are Pydantic models in `app/schemas/`. ORM models in `app/models/`.


## Backend — lint quirks

- `alembic/` is excluded from ruff (set in `pyproject.toml`).
- Ruff config lives in `pyproject.toml`.

## Backend — tests

All tests use `MagicMock` / `AsyncMock` with FastAPI `TestClient` + `dependency_overrides`. No real database needed. Located in `tests/`.

## Databases

- **Backend**: PostgreSQL (`digital_events`). Connection URL built in `app/core/config.py` from env vars. Copy `.env.example` to `.env` (defaults to `DB_HOST=localhost` for `docker compose up db`; the api container overrides it to `db`).

## Pre-commit

Installed at root: `ruff --fix` + `ruff format`. Will catch issues before commit.

