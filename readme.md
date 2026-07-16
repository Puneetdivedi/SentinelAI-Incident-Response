# SentinelAI

SentinelAI is an AI-powered incident response platform designed to help teams investigate, analyze, and respond to production incidents faster. The system combines a FastAPI backend, a React frontend, and supporting services such as PostgreSQL, Redis, and Qdrant to provide a full incident investigation workflow.

## Overview

SentinelAI aims to reduce incident investigation time by combining:

- automated investigation workflows
- multi-agent reasoning
- incident storage and retrieval
- observability and reporting
- secure authentication and admin controls

## Project Structure

- backend/: FastAPI application, services, repositories, agents, and infrastructure code
- frontend/: React + Vite user interface
- docker-compose.yml: container orchestration for the full stack
- scripts/deploy.sh: simple deployment entrypoint for hosted environments

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
- Python 3.12+ (for local backend development)
- Node.js 22+ (for local frontend development)

### Run with Docker Compose

1. Copy the environment example file:
   ```bash
   cp .env.example .env
   ```
2. Update the values in .env for your environment.
3. Start the stack:
   ```bash
   docker compose up --build -d
   ```
4. Access the application:
   - Frontend: http://localhost:5173
   - Backend health check: http://localhost:8000/health

### Local Development

#### Backend
```bash
cd backend
pip install .[dev]
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment

The repository includes a Docker Compose-based deployment flow suitable for a VPS or cloud-hosted environment.

### Host deployment

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

This script will:
- verify that .env exists
- build and start the Docker containers
- expose the frontend and backend services

## Environment Variables

Key variables include:

- JWT_SECRET_KEY
- BOOTSTRAP_ADMIN_EMAIL
- BOOTSTRAP_ADMIN_PASSWORD
- POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB
- APP_ENV
- APP_DEBUG
- LLM_PROVIDER

## Notes

- Use production values for secrets and admin credentials.
- For hosted deployments, set APP_ENV=production and APP_DEBUG=false.
- The backend includes health checks and readiness endpoints for container orchestration.

## License

This project is intended for internal or demonstration use unless otherwise specified by the repository owner.

config/

memory/

observability/

utils/

tests/

frontend/

src/

components/

pages/

hooks/

services/

layouts/

types/

contexts/

assets/

---

# MULTI AGENT DESIGN

Implement specialized agents.

Supervisor Agent

Planner Agent

Alert Analysis Agent

Log Analysis Agent

Metrics Analysis Agent

Deployment Analysis Agent

Dependency Analysis Agent

Historical Incident Agent

Correlation Agent

Root Cause Agent

Recommendation Agent

Reflection Agent

Incident Report Agent

Notification Agent

Every agent must contain:

System Prompt

Tools

Structured Outputs

Retry Logic

Confidence Score

Error Handling

Logging

---

# LANGGRAPH

Implement Supervisor Graph.

Graph flow:

START

↓

Supervisor

↓

Planner

↓

Parallel execution:

Alert Agent

Log Agent

Metrics Agent

Deployment Agent

Dependency Agent

↓

Correlation Agent

↓

Historical Incident Agent

↓

Root Cause Agent

↓

Reflection Agent

↓

Recommendation Agent

↓

Incident Report Agent

↓

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
