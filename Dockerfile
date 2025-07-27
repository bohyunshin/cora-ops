# Dockerfile
FROM python:3.11-slim

# Install system dependencies including git and uv
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Set working directory
WORKDIR /app

# Copy uv project files first (for better Docker layer caching)
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies with uv
RUN uv sync --frozen

# Copy application code
COPY src/ ./src/

# Copy pretrained weights
COPY pretrained_weight/ ./pretrained_weight/

COPY docker-entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Expose port (optional, for future web interfaces)
EXPOSE 8000


CMD ["./docker-entrypoint.sh"]
