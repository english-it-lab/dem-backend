# AGENTS.md

## Repo layout — three independent projects

| Path | Language | Package manager | Description |
|------|----------|-----------------|-------------|
| `backend/` | Python 3.12 | uv | FastAPI API + PostgreSQL (main deployable) |

Each project has its own dependencies, lockfile, and `.python-version`. Always run commands from the project directory.

## Backend — commands (all require `uv run` prefix)

```bash
cd backend
uv sync                                  # install deps into .venv
uv run uvicorn app.main:app --reload     # dev server on :8000
uv run alembic upgrade head              # apply migrations (DB must be running)
uv run alembic revision -m "..." --autogenerate  # create new migration
uv run pytest                            # run all tests (mock-based, no DB needed)
uvx ruff check --fix                     # lint
uvx ruff format                          # format
docker compose up --build                # full stack (API + PG 16)
```

## Backend — layered architecture (do NOT break)

```
adapter (FastAPI routers) -> service (business logic) -> repository (SQLAlchemy)
```

Routers import services, never repositories. Schemas are Pydantic models in `app/schemas/`. ORM models in `app/models/`.


## Backend — lint quirks

- `alembic/` is excluded from ruff (set in `pyproject.toml`).
- Ruff config lives in `backend/pyproject.toml`, not at root.

## Backend — tests

All tests use `MagicMock` / `AsyncMock` with FastAPI `TestClient` + `dependency_overrides`. No real database needed. Located in `tests/`.

## Databases

- **Backend**: PostgreSQL (`digital_events`). Connection URL built in `app/core/config.py` from env vars. Copy `.env.example` to `.env` and set `DB_HOST=localhost` for local dev (default is `db` for Docker Compose).

## Pre-commit

Installed at root: `ruff --fix` + `ruff format` (v0.11.0). Will catch issues before commit.

