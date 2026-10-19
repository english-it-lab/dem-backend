FROM python:3.12-slim

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_CACHE_DIR=/app/.uv_cache \
    UV_FROZEN=1 \
    UV_NO_DEV=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY alembic alembic
COPY app app
COPY alembic.ini main.py ./

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
