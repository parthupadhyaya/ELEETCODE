# Production image: builds the React frontend, then serves it and the API from
# one FastAPI process (backend/main.py mounts frontend/dist at /).

FROM node:22-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend /app/frontend/dist /app/frontend/dist

# Visitors' code runs in this container, so don't run it as root. The app user
# owns only the animation cache directory.
RUN useradd --create-home app && mkdir -p .cache && chown app .cache
USER app

# Render (and most hosts) pass the port in $PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
