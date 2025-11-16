.PHONY: help build up down restart logs clean test test-backend test-frontend install

help:
	@echo "Sentiment Analysis Tool - Makefile Commands"
	@echo ""
	@echo "make build          - Build all Docker containers"
	@echo "make up             - Start all services"
	@echo "make down           - Stop all services"
	@echo "make restart        - Restart all services"
	@echo "make logs           - View logs from all services"
	@echo "make logs-backend   - View backend logs"
	@echo "make logs-frontend  - View frontend logs"
	@echo "make clean          - Remove all containers, volumes, and images"
	@echo "make test           - Run all tests"
	@echo "make test-backend   - Run backend tests"
	@echo "make test-frontend  - Run frontend tests"
	@echo "make install        - Install dependencies locally"
	@echo "make shell-backend  - Open shell in backend container"
	@echo "make shell-frontend - Open shell in frontend container"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services are starting..."
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Frontend: http://localhost:3000"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

clean:
	docker-compose down -v --rmi all
	@echo "Cleaned up all containers, volumes, and images"

test:
	@echo "Running backend tests..."
	docker-compose exec backend pytest
	@echo "Running frontend tests..."
	docker-compose exec frontend npm test -- --watchAll=false

test-backend:
	docker-compose exec backend pytest -v

test-frontend:
	docker-compose exec frontend npm test -- --watchAll=false

test-backend-coverage:
	docker-compose exec backend pytest --cov=app --cov-report=html

test-frontend-coverage:
	docker-compose exec frontend npm run test:coverage

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

shell-backend:
	docker-compose exec backend /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh

ps:
	docker-compose ps

health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/api/v1/health || echo "Backend is not healthy"
	@curl -f http://localhost:3000 || echo "Frontend is not healthy"
