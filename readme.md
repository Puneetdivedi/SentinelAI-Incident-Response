# SentinelAI

SentinelAI is an enterprise-grade AI incident response platform that helps engineering and operations teams investigate production incidents faster, identify root causes, and execute remediation with confidence. It uses a modern React dashboard, a FastAPI backend, and a multi-agent orchestration layer to bring AI-driven incident reasoning into a structured, traceable workflow.

## Live Demo

**Live application:** https://sentinelai-incident-response.vercel.app

> This link points to the Vercel deployment target. The actual app becomes available once the Vercel project is configured and the GitHub auto-deploy succeeds.

## What This Project Does

SentinelAI is designed to support the full incident response lifecycle:

- Accept incident investigation requests from SREs and engineers.
- Run autonomous analysis using specialized agents.
- Correlate alerts, logs, metrics, deployments, and dependency health.
- Search historical incidents for similar failure patterns.
- Generate ranked root cause hypotheses and remediation recommendations.
- Produce executive and technical incident reports.
- Support human approval on final remediation decisions.
- Persist investigation outputs for later review and compliance.

## Industry-Level Architecture

SentinelAI follows a layered Clean Architecture structure:

- **API layer** (`backend/app/api`): FastAPI routes, request validation, and response serialization.
- **Application layer** (`backend/app/services`, `backend/app/agents`, `backend/app/graphs`, `backend/app/tools`): business orchestration, investigation workflows, agent execution, and tool integration.
- **Domain layer** (`backend/app/domain`): core incident and investigation entities, value objects, enums, and domain exceptions.
- **Infrastructure layer** (`backend/app/infrastructure`, `backend/app/repositories`): database access, Redis caching, vector search, LLM provider adapters, and mock data sources.
- **Observability and telemetry** (`backend/app/observability`): LangFuse tracing and OpenTelemetry instrumentation.

### Core architectural principles

- **Clean Architecture:** inner business rules do not depend on outer frameworks.
- **Domain-Driven Design:** domain concepts are modeled independently of transport and persistence.
- **Repository pattern:** persistence is abstracted behind repository interfaces.
- **Dependency injection:** services and routes receive dependencies from configuration.
- **Multi-agent orchestration:** a supervisor graph coordinates specialized agents and allows conditional routing.
- **Production readiness:** containerized deployment, health checks, and CI support.

## System Capabilities

### AI & orchestration

- **Supervisor Graph:** the orchestrator controlling agent execution, retry logic, and approval flows.
- **Agents:** independent units specializing in alert analysis, log analysis, metrics analysis, deployment analysis, dependency analysis, historical incident search, root cause analysis, recommendation generation, reflection, reporting, and notification drafting.
- **LangChain Tools:** reusable tools for searching logs, querying metrics, retrieving deployment history, vector-searching incident memory, executing SQL, producing markdown/PDF/Word reports, and generating charts.
- **State management:** typed investigation state captures incident details, execution plan, completed nodes, evidence, hypotheses, recommendations, logs, and trace IDs.

### Backend capabilities

- **FastAPI routes:** authentication, incident and investigation management, reports, users, health, and readiness.
- **Services:** business use cases in `backend/app/services/*` orchestrate persistence, state changes, and domain logic.
- **Data persistence:** PostgreSQL with SQLAlchemy models and Alembic migrations.
- **Cache and session stores:** Redis for rate limiting, notifications, and transient coordination.
- **Vector search:** Qdrant stores investigation memory and historical incident knowledge.
- **Security:** JWT auth with access/refresh tokens, role-based access control, and audit logging.
- **Observability:** LangFuse and OpenTelemetry instrumentation for model calls, API requests, and agent execution.

### Frontend capabilities

- **React dashboard:** provides a centralized incident operations view.
- **Pages:** Login, Dashboard, Incidents, Investigation detail, Historical incidents, Settings, and more.
- **Data fetching:** React Query and Axios for authenticated REST interaction.
- **Visualizations:** status badges, charts, incident lists, and investigation timelines.
- **Protected routes:** authenticated access and role-based safeguards.
- **Static build ready:** Vite-based production build with SPA routing support.

## File and component mapping

### Backend

- `backend/app/main.py`: application factory, startup lifecycle, logging, and CORS.
- `backend/app/config/settings.py`: environment-driven configuration with production validation.
- `backend/app/api/v1/routes/`: FastAPI route modules for `auth`, `users`, `incidents`, `investigations`, and `health`.
- `backend/app/services/`: application use cases and service orchestration.
- `backend/app/agents/`: specialized agent implementations.
- `backend/app/graphs/`: LangGraph supervisor graph and runner.
- `backend/app/tools/`: LangChain tools and toolset definitions.
- `backend/app/domain/`: enterprise core models, exceptions, enums, and value objects.
- `backend/app/repositories/`: repository interfaces and SQLAlchemy implementations.
- `backend/app/infrastructure/`: LLM provider adapters and mock data sources.
- `backend/app/observability/`: tracing and LangFuse client.
- `backend/app/middleware/`: correlation ID and error handling middleware.
- `backend/app/models/`: ORM models for users, incidents, investigations, reports, and audit logs.
- `backend/tests/`: unit, integration, graph, api, and agent tests.

### Frontend

- `frontend/src/App.tsx`: top-level route configuration.
- `frontend/src/main.tsx`: React app bootstrap.
- `frontend/src/pages/`: application screens.
- `frontend/src/services/api.ts`: Axios instance and auth token handling.
- `frontend/src/hooks/queries.ts`: server-state hooks using React Query.
- `frontend/src/contexts/AuthContext.tsx`: authentication state.
- `frontend/src/components/ProtectedRoute.tsx`: route level auth guard.
- `frontend/src/layouts/DashboardLayout.tsx`: main app layout.
- `frontend/src/components/ui.tsx`: shared UI controls and badges.
- `frontend/vercel.json`: Vercel static deployment configuration.
- `frontend/public/_redirects`: SPA redirect support.

## What makes this project industry-level

- **Modular architecture:** clean separation of API, services, domain, and infrastructure.
- **Production-first deployment:** Docker Compose, Vercel support, health checks, and CI workflows.
- **AI-driven orchestration:** multi-agent supervisor graph with retries, approvals, and resume capability.
- **Observability:** LangFuse and OpenTelemetry for tracing, and health/readiness endpoints.
- **Security:** role-based access, JWT, and configuration validation.
- **Test coverage:** unit and integration tests cover backend and graph logic.
- **Documentation:** architecture docs, deployment docs, and README guidance.

## Deployment

### Local Docker deployment

```bash
cp .env.example .env
docker compose up --build -d
```

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/health`

### Local development

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

### Vercel automatic frontend deployment

Add GitHub Actions secrets in the repository Settings → Secrets → Actions:

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

The deployment workflow is at `.github/workflows/vercel-deploy.yml`.

## Environment variables

Important variables:

- `JWT_SECRET_KEY`
- `BOOTSTRAP_ADMIN_EMAIL`
- `BOOTSTRAP_ADMIN_PASSWORD`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `APP_ENV`
- `APP_DEBUG`
- `LLM_PROVIDER`
- `VITE_API_BASE_URL`

## Recommended next steps

1. Configure a real backend host and set `VITE_API_BASE_URL` in Vercel.
2. Add production-grade data providers for logs, metrics, and deployments.
3. Replace mock datasources with real observability connectors.
4. Add role-specific dashboards and approval workflows for SRE and business users.

## License

This project is intended for internal and demo use unless otherwise specified by the repository owner.

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
