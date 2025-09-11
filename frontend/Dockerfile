# Build the TypeScript client library
FROM node:20-alpine AS build
WORKDIR /app

# Copy sources for both client lib and frontend app
COPY client /app/client
COPY frontend /app/frontend

# Install and build the React frontend (imports client source via alias)
RUN npm --prefix /app/frontend install --legacy-peer-deps
RUN npm --prefix /app/frontend run build

# Serve built app with Nginx and proxy /api to the backend
FROM nginx:alpine AS runtime

# Copy built assets
COPY --from=build /app/frontend/dist/ /usr/share/nginx/html/

# Configure Nginx to proxy API calls to backend service
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
