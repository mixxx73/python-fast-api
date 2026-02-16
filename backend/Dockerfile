FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application
COPY backend/app /app/app
# Copy Alembic configuration and migrations
COPY backend/alembic.ini /app/alembic.ini
COPY backend/migrations /app/migrations
# Copy pytest / tool config so asyncio_mode = "auto" is picked up in tests
COPY backend/pyproject.toml /app/pyproject.toml

# Default DB URL points to docker-compose service "db"
ENV DATABASE_URL=postgresql+asyncpg://app:app@db:5432/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
