FROM postgres:16-alpine

# Default environment variables (override at runtime as needed)
ENV POSTGRES_USER=app \
    POSTGRES_PASSWORD=app \
    POSTGRES_DB=app

# Expose the default Postgres port
EXPOSE 5432

# Optionally copy initialization scripts into the entrypoint dir
# Uncomment and add SQL files to `infra/db/` if needed.
# COPY infra/db/*.sql /docker-entrypoint-initdb.d/

# The official image provides the default command/entrypoint.

