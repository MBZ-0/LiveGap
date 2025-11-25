# syntax=docker/dockerfile:1
# another.ai backend Dockerfile
# Production container with FastAPI + Playwright Chromium.

ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION} AS base

# Environment configuration
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true \
    AGENT_MAX_SECONDS=30 \
    AGENT_NAV_TIMEOUT=10000

# System dependencies for Chromium / Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget xvfb \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libxkbcommon0 libxrandr2 libxdamage1 \
    libxcomposite1 libxfixes3 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Dependency install (cached if requirements unchanged)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m playwright install --with-deps chromium

# Copy application code (only what we need for runtime)
COPY app ./app

# Adjust ownership (if running as non-root)
RUN chown -R app:app /app
USER app

EXPOSE 8000

# Healthcheck: FastAPI /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import httpx,sys; sys.exit(0 if httpx.get('http://127.0.0.1:8000/health').status_code==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
