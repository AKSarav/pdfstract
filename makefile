.PHONY: models build up down logs clean status rebuild

## Download ML models on host - Run only if the models are not already downloaded
models:
	@if [ ! -d "hf-cache/PDF-Extract-Kit-1.0" ]; then \
		echo "📦 Downloading MinerU models..."; \
		python scripts/mineru-setup.py; \
	else \
		echo "📦 MinerU models already downloaded"; \
	fi

## Build docker image
build: models
	@echo "🐳 Building Docker image..."
	@docker compose build --no-cache

## Start services
up: build
	@echo "🚀 Starting services..."
	@docker compose up -d

## Stop services
down:
	@echo "🛑 Stopping services..."
	@docker compose down

## Tail logs
logs:
	@docker compose logs -f

## Clean everything (careful!)
clean:
	@echo "🧹 Cleaning containers and images..."
	@docker compose down -v

## Show status
status:
	@docker compose ps

## Rebuild without cache
rebuild:
	@echo "🔄 Rebuilding from scratch..."
	@docker compose build --no-cache
	@docker compose up -d