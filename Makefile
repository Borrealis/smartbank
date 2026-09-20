.PHONY: help install lint format test run ingest build clean

help:
	@echo "install - sync dependencies"
	@echo "lint - ruff check"
	@echo "format - ruff format"
	@echo "test - run pytest"
	@echo "run - start all services with Docker Compose"
	@echo "build - docker compose build"
	@echo "clean - remove caches"
	@echo "ingest - load documents into pgvector"

install:
	uv sync
	cd gateway && uv sync
	cd worker && uv sync

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	cd gateway && uv run pytest -v
	cd worker && uv run pytest -v

run:
	docker compose up
ingest:
	PYTHONPATH=worker uv run --project worker python -m worker_scripts.ingest_docs

build:
	docker compose build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache
