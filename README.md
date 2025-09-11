# Expense Settlement Service

[![CI](https://github.com/mixxx73/ai-work-i1/actions/workflows/ci.yml/badge.svg)](https://github.com/mixxx73/ai-work-i1/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mixxx73/ai-work-i1/branch/main/graph/badge.svg)](https://codecov.io/gh/mixxx73/ai-work-i1)

This repository provides a skeleton for an expense splitting application.
It demonstrates a FastAPI backend designed with domain-driven design (DDD)
principles, a TypeScript client library, a minimal frontend, and Terraform
infrastructure configuration.

## Directory Structure

- `backend/` – FastAPI service and domain logic
- `client/` – TypeScript client library targeting the API
- `frontend/` – Example TypeScript frontend consuming the client library
- `infra/` – Infrastructure as code using Terraform
- `docs/` – Project documentation

## Local Development

### Backend

```bash
cd backend
# Create and use a Pipenv environment
pipenv install -r requirements.txt

# Option 1: run commands via pipenv
pipenv run uvicorn app.main:app --reload

# Option 2: activate a shell, then run normally
# pipenv shell
# uvicorn app.main:app --reload
```

#### Backend (Docker)

Use Docker Compose to run the API and Postgres locally without setting up Python:

```bash
# From the repository root
docker compose up -d

# Tail logs (optional)
docker compose logs -f backend

# API available at
#   http://localhost:8000
#   http://localhost:8000/docs

# Connect to Postgres from host
#   Host:     localhost
#   Port:     15432
#   User:     app
#   Password: app
#   Database: app
# Example:
# psql -h localhost -p 15432 -U app app

# Stop services
docker compose down

# Rebuild backend image after dependency changes
docker compose build backend
```

### Frontend (Docker)

Run the minimal UX along with the backend using Docker Compose:

```bash
# From the repository root
docker compose up -d frontend backend db

# Open the minimal UI
open http://localhost:8080  # macOS
# xdg-open http://localhost:8080  # Linux
# Or browse manually
```

Notes:
- The frontend proxies API requests to the backend using the `/api` path via Nginx, avoiding CORS issues.
- React app provides a login screen and a simple home view with a profile component.

#### Frontend Tests (Docker)

Run frontend unit tests (SSR smoke) in a container:

```bash
# From the repository root
make frontend-test
# or
docker compose --profile test run --rm frontend-tests
```

Notes:
- Tests build a minimal test bundle (`tsc -p frontend/tsconfig.test.json`) then run Node’s test runner with an alias loader that stubs `@client`.
- No backend is required for these tests.

#### Watch frontend changes (Docker)

Rebuild and restart the frontend container automatically when source files change:

```bash
# Ensure services are running
docker compose up -d frontend backend db

# In another terminal, start watch mode for the frontend
docker compose watch frontend

# Edit files under ./frontend or ./client to trigger a rebuild
```

Notes:
- This uses Docker Compose watch to rebuild the image on changes (not HMR).
- For hot reload during local dev, run Vite: `npm --prefix frontend run dev`.

Login
- First, create a user via API or add one in DB.
- Use the login screen with email/password; upon success you will see your profile.

### Client Library

```bash
cd client
npm install
npm test
```

### Frontend

```bash
cd frontend
npm test
```

## Testing

Run all checks from the repository root:

```bash
# Python backend (with coverage)
(cd backend && pipenv run pytest --cov=app --cov-report=term-missing tests)

# Client and frontend
npm --prefix client test
npm --prefix frontend test
```

### Backend Tests (Docker)

Run backend unit tests in Docker (no local Python needed):

```bash
# Build images if not built yet
docker compose build backend

# Run tests inside the backend container
docker compose run --rm backend pytest -q --cov=app --cov-report=term-missing tests

# Generate XML coverage for CI-like runs (optional)
docker compose run --rm backend pytest -q --cov=app --cov-report=xml --cov-report=term tests
```

Notes:
- Tests use an in-memory SQLite database and do not require the Postgres container.
- You can run them without `docker compose up`; `docker compose run --rm backend ...` is enough.

Coverage uploads
- CI uploads coverage to Codecov using `codecov/codecov-action@v4`.
- For private repos, add a `CODECOV_TOKEN` repository secret.

GitHub Actions runs flake8 and backend tests on every push/PR.

## Security Considerations

- Use environment variables for secrets and database credentials.
- Configure authentication and authorization for all endpoints.
- Apply least privilege to infrastructure resources.

## Documentation

Additional docs are available in the `docs/` directory.
