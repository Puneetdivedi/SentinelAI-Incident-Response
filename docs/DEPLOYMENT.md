# Deployment Guide

This document explains how to deploy SentinelAI locally and how to configure the project for Vercel frontend hosting.

## Local development

### 1. Backend

From the repository root:

```bash
cd backend
python -m pip install --upgrade pip
pip install .[dev]
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000` and the API at `http://localhost:8000/api/v1`.

### 2. Frontend

From the repository root:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

The frontend will be available at `http://localhost:5173`.

### 3. Optional Docker Compose deployment

This repository includes a Docker Compose configuration for local full-stack deployment.

```bash
cp .env.example .env
# Edit .env and set secure values for production mode.
docker compose up --build -d
```

Then visit:

- Backend health: `http://localhost:8000/health`
- Frontend: `http://localhost:5173`

## Vercel deployment (frontend)

The frontend is configured for static deployment on Vercel with `frontend/vercel.json`.

### Required secrets

Add these secrets to the GitHub repository or Vercel project:

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `VITE_API_BASE_URL` (as a Vercel Environment Variable)

### Vercel environment variable

Set `VITE_API_BASE_URL` to the backend API URL, for example:

```text
https://api.example.com/api/v1
```

### GitHub Action

This repository includes `.github/workflows/vercel-deploy.yml` to deploy the frontend after each push to `main`.

### Backend hosting

The backend is not deployed automatically by Vercel. Use a separate host or container deployment for the backend and point the frontend at its public API endpoint via `VITE_API_BASE_URL`.

## Production readiness checklist

- [ ] Set `APP_ENV=production` in your backend environment
- [ ] Set a secure `JWT_SECRET_KEY`
- [ ] Configure correct `DATABASE_URL`, `REDIS_URL`, and `QDRANT_URL`
- [ ] Set `BOOTSTRAP_ADMIN_EMAIL` and `BOOTSTRAP_ADMIN_PASSWORD`
- [ ] Configure `VITE_API_BASE_URL` for the frontend
- [ ] Add `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` if observability is required
- [ ] Add `OTEL_EXPORTER_OTLP_ENDPOINT` if using OpenTelemetry

## Notes

- `frontend/public/_redirects` ensures SPA routing works on Vercel.
- `frontend/vercel.json` tells Vercel to build the static site and route all requests to `index.html`.
- The GitHub Action only deploys the frontend; the backend must be available separately.
