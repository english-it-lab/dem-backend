# Digital Event Manager API

FastAPI + PostgreSQL backend bootstrapped with **uv**, **SQLAlchemy 2.0**, and **Alembic**. The codebase follows a layered layout (repository → service → adapter) so that persistence, business rules, and delivery stay isolated.

## Requirements
- Python 3.12
- [uv](https://github.com/astral-sh/uv) (already recorded via `pyproject.toml` + `uv.lock`)
- Docker (optional but recommended for local infra)

## Quick start
```bash
uv sync && cp .env.example .env
docker compose up db -d
uv run alembic upgrade head && uv run uvicorn app.main:app --reload
```
API: `http://localhost:8000`, Swagger UI: `http://localhost:8000/docs`.

Use `uv run <command>` to execute anything inside the virtual environment.

## Project layout
```
app/
  adapters/api        # FastAPI routers + dependencies (delivery layer)
  core                # configuration
  db                  # async engine and sessions
  models              # SQLAlchemy ORM models (metadata used by Alembic)
  repositories        # persistence layer
  schemas             # Pydantic DTOs
  services            # business logic layer
alembic/              # migration environment + versions
tests/                # pytest suite (mock-based, no database needed)
docs/                 # technical specification and project charters
Dockerfile            # production image built with uv
```

## Run modes
| Mode | Command | Notes |
|------|---------|-------|
| DB in Docker, API local (default) | `docker compose up db -d` + `uv run uvicorn app.main:app --reload` | `.env` has `DB_HOST=localhost`; fastest reload |
| Everything in Docker | `docker compose up --build` | api container forces `DB_HOST=db`, mounts `app/` and reloads on change |

Postgres is published on `localhost:5432` with the credentials from `.env`.

The frontend reaches the API through a proxy on a relative `/api/v1` path (Vite dev server or nginx), so no CORS setup is needed for the default ports. For direct browser calls from another origin, add it to `CORS_ORIGINS` in `.env` (comma-separated).

## Database migrations
```bash
# create a new revision
uv run alembic revision --autogenerate -m "short message"

# apply migrations
uv run alembic upgrade head

# apply inside the running docker compose stack
docker compose exec api uv run alembic upgrade head
```
Alembic already knows about the async metadata via `app.models.Base`.

## Sample flow (Universities)
1. **Schema** – `app/schemas/university.py`
2. **Repository** – `app/repositories/university.py`
3. **Service** – `app/services/university.py`
4. **Adapter** – `app/adapters/api/v1/universities.py`

When adding new features/entities, repeat the same pattern so that routers depend only on services and never on repositories directly.

## Tests and linting
```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

## Swagger UI

After starting the API server, you can open the interactive Swagger UI in your browser:

```bash
http://localhost:8000/docs
```
