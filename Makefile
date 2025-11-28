.PHONY: help init install migrate test run docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make init          - Initialize project (copy .env.sample to .env)"
	@echo "  make install       - Install dependencies"
	@echo "  make migrate       - Run database migrations"
	@echo "  make test          - Run tests"
	@echo "  make run           - Run development server"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make clean         - Remove Python cache files"

init:
	@echo "Initializing project..."
	@cp .env.sample .env
	@echo "✓ Created .env file from .env.sample"
	@echo "⚠ Please update .env with your actual database credentials"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

migrate:
	@echo "Running migrations..."
	python manage.py migrate
	@echo "✓ Migrations completed"

test:
	@echo "Running tests..."
	python manage.py test
	@echo "✓ Tests completed"

run:
	@echo "Starting development server..."
	python manage.py runserver

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up --build

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✓ Cache cleaned"