.PHONY: build run stop clean logs install

# Install dependencies with uv
install:
	uv sync

# Run locally (requires OpenSearch running)
run-local:
	uv run db/main.py

# Build the Docker image
build:
	docker build -t opensearch-python-example .

# Run with Docker Compose (recommended)
run:
	docker-compose up --build

# Run with Docker Compose in detached mode
run-detached:
	docker-compose up -d --build

# Stop all services
stop:
	docker-compose down

# Clean up containers and images
clean:
	docker-compose down -v
	docker system prune -f

# View logs
logs:
	docker-compose logs -f

# Run just OpenSearch
opensearch-only:
	@echo "Cleaning up any existing OpenSearch container..."
	docker stop opensearch-node 2>/dev/null || true
	docker rm opensearch-node 2>/dev/null || true
	@echo "Starting OpenSearch..."
	docker run -d \
		--name opensearch-node \
		-p 9200:9200 -p 9600:9600 \
		-e "discovery.type=single-node" \
		-e "DISABLE_SECURITY_PLUGIN=true" \
		-e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" \
		opensearchproject/opensearch:2.11.0
	@echo "OpenSearch API: http://localhost:9200"

# Run OpenSearch + Dashboards (Web UI)
opensearch-with-ui:
	@echo "Cleaning up any existing containers..."
	docker stop opensearch-dashboards opensearch-node 2>/dev/null || true
	docker rm opensearch-dashboards opensearch-node 2>/dev/null || true
	docker network create opensearch-net 2>/dev/null || true
	@echo "Starting OpenSearch..."
	docker run -d \
		--name opensearch-node \
		--network opensearch-net \
		-p 9200:9200 -p 9600:9600 \
		-e "discovery.type=single-node" \
		-e "DISABLE_SECURITY_PLUGIN=true" \
		-e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" \
		opensearchproject/opensearch:2.11.0
	@echo "Waiting for OpenSearch to start..."
	@sleep 15
	@echo "Starting OpenSearch Dashboards..."
	docker run -d \
		--name opensearch-dashboards \
		--network opensearch-net \
		-p 5601:5601 \
		-e "OPENSEARCH_HOSTS=http://opensearch-node:9200" \
		-e "DISABLE_SECURITY_DASHBOARDS_PLUGIN=true" \
		opensearchproject/opensearch-dashboards:2.11.0
	@echo ""
	@echo "Setup complete!"
	@echo "OpenSearch API: http://localhost:9200"
	@echo "Web Dashboard: http://localhost:5601"
	@echo "Dashboards may take 30-60 seconds to fully load"

# Stop and remove OpenSearch container
stop-opensearch:
	docker stop opensearch-node && docker rm opensearch-node

# Stop OpenSearch + Dashboards
stop-opensearch-ui:
	docker stop opensearch-dashboards opensearch-node || true
	docker rm opensearch-dashboards opensearch-node || true
	docker network rm opensearch-net || true

# Test connection to OpenSearch
test:
	curl -X GET "localhost:9200/_cluster/health?pretty"

# Add dependencies with uv
add-dep:
	uv add $(DEP)

# Remove dependencies with uv
remove-dep:
	uv remove $(DEP)

# Show help
help:
	@echo "Available commands:"
	@echo "  install             - Install dependencies with uv"
	@echo "  run-local           - Run locally (requires OpenSearch running)"
	@echo "  build               - Build Docker image"
	@echo "  run                 - Run with Docker Compose"
	@echo "  run-detached        - Run with Docker Compose in background"
	@echo "  stop                - Stop all services"
	@echo "  clean               - Clean up containers and images"
	@echo "  logs                - View logs"
	@echo "  opensearch-only     - Run just OpenSearch container"
	@echo "  opensearch-with-ui  - Run OpenSearch + Web UI (Dashboards)"
	@echo "  stop-opensearch     - Stop OpenSearch container"
	@echo "  stop-opensearch-ui  - Stop OpenSearch + Dashboards"
	@echo "  test                - Test OpenSearch connection"
	@echo "  add-dep DEP=name    - Add dependency with uv"
	@echo "  remove-dep DEP=name - Remove dependency with uv"
