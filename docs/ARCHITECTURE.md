# Architecture

The project is organized using domain-driven design principles:

- **Domain** – business entities and repository interfaces live in `backend/app/domain`.
- **Infrastructure** – database and repository implementations live in `backend/app/infrastructure`.
- **API** – FastAPI routers expose application functionality in `backend/app/api`.

The frontend and client library interact with the backend through HTTP
requests defined by the client library.
