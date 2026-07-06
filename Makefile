.PHONY: install test lint format clean mock

install:
	@echo "Installing dependencies with uv..."
	uv venv
	uv pip install -e .
	uv run pre-commit install

test:
	@echo "Running unit tests..."
	uv run bash -c "PYTHONPATH=src pytest tests/"

lint:
	@echo "Running linting..."
	uv run ruff check .

format:
	@echo "Running formatting..."
	uv run ruff format .

mock:
	@echo "Running scraper in mock mode..."
	uv run src/__main__.py --mock

clean:
	@echo "Cleaning up..."
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
