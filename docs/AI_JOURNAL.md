# AI Usage Report

- **Tools Used:** Codex cli interface
- **Prompts:** Generated project skeleton with FastAPI backend, TypeScript client and frontend, and Terraform infrastructure. Use Instruction.md file as reference.
- **Challenges:** Structuring the project to follow DDD principles across multiple components.

- **Latest steps:**
  - Added FastAPI backend with DDD layering (domain models/services, infrastructure repositories/ORM, API routers for auth/users/groups/expenses).
  - Implemented JWT auth with password hashing (bcrypt) and request guards; added signup/login/me endpoints.
  - Set up SQLAlchemy ORM models and Alembic migrations; auto-create tables on startup for dev.
  - Wrote pytest test suite using in-memory SQLite with fixtures; enabled coverage via pytest-cov.
  - Created Docker Compose stack: Postgres service and backend container with hot reload and `alembic upgrade head` on start.
  - Added backend Dockerfile, requirements, Pipenv files, and flake8/coverage configs.
  - Updated README with local dev (pipenv and Docker), testing, and Codecov notes.
  - Added GitHub Actions CI (flake8, tests, coverage upload) and Codecov integration.
  - Scaffolded TypeScript client and frontend packages (basic structure and tests placeholders).
  - Added Terraform `infra/` skeleton.

- **Example prompts and iterations (summarized):**
  - "Design a FastAPI service using DDD. Create domain models (User, Group, Expense), repositories, services, and API routers. Include SQLAlchemy and Alembic."
  - "Implement authentication: signup, login returning JWT, and /auth/me. Use passlib[bcrypt] for hashing and PyJWT for tokens."
  - "Create SQLAlchemy ORM models and many-to-many relationship for group members; generate initial Alembic migrations."
  - "Add endpoints for users, groups (create, add member, list), and expenses (create, list, get) with basic validation and error handling."
  - "Write pytest tests for auth, users, groups, expenses. Use in-memory SQLite with fixtures and provide coverage output."
  - "Add Dockerfile for backend and docker-compose with Postgres. Run alembic upgrade then start uvicorn with reload."
  - "Set up GitHub Actions: install with pipenv, run flake8, run pytest with coverage, upload to Codecov."
  - "Create minimal TypeScript client and frontend scaffolds with package.json, tsconfig, and placeholder tests."
  - "Author README covering local dev (pipenv/docker), testing, and CI; add SECURITY and ARCHITECTURE docs."

  Note: These are representative summaries of the prompts used to drive the implementation, not verbatim transcripts.
