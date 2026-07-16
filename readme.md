# SentinelAI

SentinelAI is an enterprise-style AI incident response platform designed to accelerate production incident investigation, root cause analysis, and remediation planning. It combines a modern React frontend, a FastAPI backend, and supporting infrastructure services to give teams a practical, production-ready incident command experience.

## Live Demo

Live application: https://sentinelai-incident-response.vercel.app

> Note: This URL is configured as the intended Vercel deployment target. It will become active once the Vercel project is created, the first deployment succeeds, and the `VERCEL_TOKEN`/project secrets are configured.

## What This Project Does

SentinelAI helps engineering and operations teams:

- investigate incidents with AI-assisted reasoning
- correlate alerts, logs, metrics, deployments, and dependencies
- generate structured incident summaries and recommendations
- store investigation context for future analysis
- provide a web-based workspace for fast collaboration during incidents

## Core Features

- AI-powered incident investigation workflow
- multi-agent reasoning architecture
- health and readiness monitoring endpoints
- secure authentication and bootstrap admin support
- Docker-based deployment for local and hosted environments
- observability and reporting hooks for production use

## Architecture Overview

The platform is organized into:

- Backend: FastAPI, SQLAlchemy, Alembic, Pydantic, Redis, PostgreSQL, Qdrant, LangChain/LangGraph
- Frontend: React, TypeScript, Vite, Tailwind CSS, React Query, Axios
- Infrastructure: Docker Compose with PostgreSQL, Redis, Qdrant, backend, and frontend services

## Project Structure

- backend/: FastAPI application, services, repositories, agents, and infrastructure code
- frontend/: React + Vite user interface
- docker-compose.yml: container orchestration for the full stack
- scripts/: deployment and quality-check utilities
- docs/: architecture and project documentation

## Tech Stack

### Backend
- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Redis
- PostgreSQL
- Qdrant
- LangChain / LangGraph
- OpenTelemetry
- JWT-based authentication

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- React Query
- Axios
- Recharts

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ for backend development
- Node.js 22+ for frontend development

### Run Locally with Docker Compose

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Update the values in .env for your environment.
3. Start the stack:
   ```bash
   docker compose up --build -d
   ```
4. Open the application:
   - Frontend: http://localhost:5173
   - Backend health check: http://localhost:8000/health

### Run Backend Locally

```bash
cd backend
pip install .[dev]
uvicorn app.main:app --reload
```

### Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

## Deployment

The repository includes a Docker Compose deployment flow designed for a VPS, cloud VM, or similar hosted environment.

### Deploy with the included script

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

This script will:
- verify that .env exists
- build and start the Docker containers
- expose the frontend and backend services

## Automatic Vercel deploy (GitHub Actions)

This repository includes a GitHub Actions workflow that will automatically build and deploy the `frontend` folder to Vercel on pushes to `main`.

Required GitHub repository secrets (add at Settings → Secrets → Actions):

- `VERCEL_TOKEN` — your personal Vercel token (required)
- `VERCEL_ORG_ID` — your Vercel organization ID (recommended)
- `VERCEL_PROJECT_ID` — your Vercel project ID (recommended)

Once those secrets are set the action `.github/workflows/vercel-deploy.yml` will run and publish to Vercel.

If you prefer to manage deployments from the Vercel dashboard, import the repo there and set the project root to `frontend`.

## Environment Variables

Key environment variables include:

- JWT_SECRET_KEY
- BOOTSTRAP_ADMIN_EMAIL
- BOOTSTRAP_ADMIN_PASSWORD
- POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB
- APP_ENV
- APP_DEBUG
- LLM_PROVIDER

## Quality and Reliability

The project includes:

- linting and test automation support
- health and readiness endpoints for orchestration
- containerized deployment readiness
- production-oriented configuration validation

## Notes

- Use strong production secrets for all hosted deployments.
- Set APP_ENV=production and APP_DEBUG=false for live environments.
- The backend health endpoint and readiness endpoint are available for monitoring and container health checks.

## License

This project is intended for internal, demo, or portfolio use unless otherwise specified by the repository owner.

Human Approval Node

↓

Notification Agent

↓

Persist Investigation

↓

END

Support conditional routing, retries, and resumable execution.

---

# STATE MANAGEMENT

Design a strongly typed LangGraph state containing:

Incident ID

Incident Description

Execution Plan

Current Node

Completed Nodes

Logs

Alerts

Metrics

Deployments

Dependencies

Historical Matches

Root Cause Candidates

Recommendations

Incident Timeline

Confidence Scores

Errors

Retry Count

Human Approval Status

Generated Reports

Trace IDs

LangFuse Run IDs

---

# LANGCHAIN TOOLS

Implement reusable tools for:

Log Search

Metrics Query

Deployment History

Incident Search

Vector Search

Python Execution

SQL Query

Markdown Report

PDF Report

Word Report

Chart Generation

Timeline Generator

Notification Generator

---

# DATA SOURCES

Support:

Mock Kubernetes logs

Mock Nginx logs

Mock FastAPI logs

Mock PostgreSQL logs

CPU metrics

Memory metrics

Latency metrics

Deployment history

Incident history

Knowledge Base

The application must work completely with mock data first.

Design interfaces so real providers can later replace mocks.

---

# ROOT CAUSE ANALYSIS

The AI should identify possible causes such as:

Memory Leak

Database Lock

Connection Pool Exhaustion

Redis Timeout

Bad Deployment

Configuration Error

DNS Failure

Certificate Expiration

Dependency Failure

External API Failure

Each hypothesis must include:

Confidence

Evidence

Supporting Logs

Supporting Metrics

Reasoning

Recommended Actions

---

# RECOMMENDATIONS

Generate remediation such as:

Rollback Deployment

Restart Service

Scale Pods

Increase Connection Pool

Flush Cache

Restart Database

Rotate Certificates

Investigate SQL Queries

Open Incident

Escalate to Team

Each recommendation must include priority, risk, and justification.

---

# REPORTS

Generate:

Executive Summary

Incident Timeline

Evidence

Root Cause

Business Impact

Technical Impact

Recommendations

Action Items

Lessons Learned

Support PDF, DOCX, and Markdown export.

---

# FRONTEND

Build an enterprise dashboard with:

Login

Dashboard

Live Incidents

Chat Investigation

Agent Execution Graph

Timeline

Root Cause View

Recommendations

Reports

Historical Incidents

LangFuse Trace Viewer

Settings

Use modern responsive UI.

---

# LANGFUSE

Instrument every LLM interaction.

Capture:

Prompt Versions

Agent Names

Execution Graph

Latency

Token Usage

Cost

Failures

Retries

Feedback

Session IDs

Trace IDs

Provide a trace link for each investigation.

---

# OBSERVABILITY

Add structured logging, health endpoints, metrics, and distributed tracing.

---

# TESTING

Use pytest.

Include:

Unit Tests

Integration Tests

Graph Tests

Agent Tests

API Tests

---

# SECURITY

Implement:

JWT

RBAC

Input Validation

SQL Injection Protection

Prompt Injection Mitigation

Rate Limiting

Audit Logs

---

# DEPLOYMENT

Provide:

Dockerfile

docker-compose.yml

GitHub Actions

Environment Variables

README

Architecture Diagram

API Documentation

Deployment Guide

---

# DEVELOPMENT RULES

Never generate placeholder code.

Never skip files.

Never leave TODO comments.

Generate fully functional implementations.

Keep architecture consistent.

Use proper typing.

Use async where appropriate.

Follow SOLID principles.

Write production-quality code.

---

# IMPLEMENTATION STRATEGY

Do NOT generate the entire project in one response.

Instead, follow this exact sequence:

Phase 1 – High-level architecture and folder structure.

Phase 2 – Database schema, domain models, and configuration.

Phase 3 – Authentication and user management.

Phase 4 – LangGraph state, graph orchestration, and supervisor.

Phase 5 – Individual agents.

Phase 6 – LangChain tools.

Phase 7 – APIs.

Phase 8 – Frontend.

Phase 9 – LangFuse instrumentation.

Phase 10 – Docker, CI/CD, tests, and documentation.

After completing each phase, stop and wait for my approval before moving to the next phase.

At every phase, ensure all generated code compiles and integrates cleanly with the previous phases.
