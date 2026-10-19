# Бэкенд (Digital Event Manager API)

FastAPI + PostgreSQL. Зависимости — **uv**, ORM — **SQLAlchemy 2.0** (async), миграции — **Alembic**. Код разбит на слои (repository → service → adapter), чтобы хранение, бизнес-правила и HTTP-доставка не смешивались.

## Требования

- Python 3.12 (версия закреплена в `.python-version`)
- [uv](https://github.com/astral-sh/uv) — зависимости описаны в `pyproject.toml` + `uv.lock`
- Docker — для PostgreSQL (и, по желанию, для запуска всего стека)

## Быстрый старт

```bash
uv sync && cp .env.example .env
docker compose up db -d
uv run alembic upgrade head && uv run uvicorn app.main:app --reload
```

API: `http://localhost:8000`, Swagger UI: `http://localhost:8000/docs`.

Любую команду внутри виртуального окружения запускайте через `uv run <команда>`.

## Структура проекта

```
app/
  adapters/api        # роутеры FastAPI + DI-зависимости (слой доставки)
  core                # конфигурация
  db                  # async engine и сессии
  models              # ORM-модели SQLAlchemy (metadata для Alembic)
  repositories        # слой хранения
  schemas             # Pydantic DTO
  services            # бизнес-логика
alembic/              # окружение миграций + версии
tests/                # pytest (на моках, база не нужна)
docs/                 # техническое задание и уставы проекта
Dockerfile            # production-образ на uv
```

Подробная карта и правила для участников — в `AGENTS.md`.

## Режимы запуска

| Режим | Команда | Примечания |
|-------|---------|------------|
| БД в Docker, API локально (по умолчанию) | `docker compose up db -d` + `uv run uvicorn app.main:app --reload` | в `.env` стоит `DB_HOST=localhost`; самый быстрый hot-reload |
| Всё в Docker | `docker compose up --build` | контейнер api сам ставит `DB_HOST=db`, монтирует `app/` и перезапускается при изменениях; миграции применяются на старте |

PostgreSQL опубликован на `localhost:5432` с учётными данными из `.env`.

Фронтенд ходит в API через прокси по относительному пути `/api/v1` (dev-сервер Vite или nginx), поэтому для стандартных портов CORS настраивать не нужно. Если браузер обращается к API напрямую с другого origin, добавьте его в `CORS_ORIGINS` в `.env` (через запятую).

## Миграции

```bash
# создать новую ревизию после изменения app/models
uv run alembic revision --autogenerate -m "короткое описание"

# применить миграции
uv run alembic upgrade head

# применить внутри запущенного docker compose
docker compose exec api uv run alembic upgrade head
```

Alembic берёт metadata из `app.models.Base`. Проверяйте сгенерированный diff: autogenerate не видит переименования и часть ограничений.

## Как добавить сущность (на примере университетов)

1. **Схема** — `app/schemas/__init__.py` (все DTO в одном файле: `UniversityBase` / `UniversityCreate` / `UniversityRead` / `UniversityUpdate`)
2. **Репозиторий** — `app/repositories/university.py`
3. **Сервис** — `app/services/university.py`
4. **Фабрика** — `get_university_service` в `app/adapters/api/dependencies.py`
5. **Роутер** — `app/adapters/api/v1/universities.py`, подключение в `app/adapters/api/v1/__init__.py`
6. **Тесты** — `tests/api/test_universities.py`

Роутеры зависят только от сервисов и никогда не обращаются к репозиториям напрямую.

## Тесты и линтер

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

CI (`.github/workflows/ci.yml`) гоняет `ruff format --check`, `ruff check` и `pytest` на каждом PR; на push в `main` дополнительно собирается Docker-образ. Деплоя нет — сервер не арендуется.

## Swagger UI

После запуска сервера интерактивная документация доступна по адресу `http://localhost:8000/docs`.
