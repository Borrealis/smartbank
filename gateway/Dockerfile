FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Заменяем копирование корневых файлов на файлы шлюза:
COPY gateway/pyproject.toml gateway/uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project

COPY gateway/alembic.ini ./
COPY gateway/alembic/ ./alembic/
COPY gateway/app/ ./app/

EXPOSE 8000
ENV PATH="/app/.venv/bin:$PATH"
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
