# AniVibe Makefile

.PHONY: help install install-benchmark dev test test-benchmark lint format clean prepare-data evaluate benchmark-report benchmark docker-build docker-up docker-down migrate db-setup

help:
	@echo "AniVibe - Makefile Commands"
	@echo "======================================"
	@echo "install        - Install dependencies"
	@echo "dev            - Run development server"
	@echo "test           - Run tests"
	@echo "test-benchmark - Run offline recommender tests"
	@echo "prepare-data   - Prepare sample benchmark data"
	@echo "evaluate       - Evaluate baseline recommenders"
	@echo "benchmark      - Prepare data, evaluate models, and generate report"
	@echo "lint           - Run linting"
	@echo "format         - Format code"
	@echo "clean          - Clean cache and build files"
	@echo "docker-build   - Build Docker images"
	@echo "docker-up      - Start Docker services"
	@echo "docker-down    - Stop Docker services"
	@echo "migrate        - Run database migrations"
	@echo "db-setup       - Setup database with initial data"

install:
	pip install -r requirements.txt

install-benchmark:
	pip install -r requirements-benchmark.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=html

test-benchmark:
	pytest tests/test_offline_recommender.py -v

prepare-data:
	python -m scripts.prepare_dataset --sample

evaluate:
	python -m scripts.evaluate_recommenders --config configs/eval.yaml

benchmark-report:
	python -m scripts.generate_report

benchmark: prepare-data evaluate benchmark-report

lint:
	flake8 app/ --max-line-length=120
	mypy app/

format:
	black app/ tests/ --line-length=100
	isort app/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "MLflow: http://localhost:5000"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

migrate:
	alembic upgrade head

db-setup:
	python scripts/setup_database.py

# Quick start
start: docker-up
	@echo "🚀 AniVibe is running!"

stop: docker-down
	@echo "⏹️  AniVibe stopped"

restart: stop start
	@echo "🔄 AniVibe restarted"

# Development workflow
dev-setup: install db-setup
	@echo "✅ Development environment ready!"

# Production deployment
deploy:
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d --build
