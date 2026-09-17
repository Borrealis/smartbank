FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Заменяем копирование корневых файлов на файлы шлюза:
COPY worker/pyproject.toml worker/uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project


COPY worker/app/ ./app/

ENV PATH="/app/.venv/bin:$PATH"
CMD ["faststream", "run", "app.main:app"]
