.PHONY: help install lint format test run build clean

help:
	@echo "install - sync dependencies"
	@echo "lint - ruff check"
	@echo "format - ruff format"
	@echo "test - run pytest"
	@echo "run - start uvicorn locally"
	@echo "build - docker compose build"
	@echo "clean - remove caches"

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
	cd gateway && uv run uvicorn app.main:app --reload


build:
	docker compose build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache
