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

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest -v

run:
	uv run uvicorn app.main:app --reload

build:
	docker compose build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache