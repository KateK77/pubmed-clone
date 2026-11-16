FROM node:22-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_DEBUG=0
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ backend/
COPY --from=frontend /build/frontend/dist frontend/dist
RUN useradd --create-home app
USER app
EXPOSE 8000
CMD ["gunicorn", "--chdir", "backend", "medresearch.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "120", "--access-logfile", "-"]
