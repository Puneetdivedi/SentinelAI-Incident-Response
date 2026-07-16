# SentinelAI

SentinelAI is an enterprise-grade AI incident response platform that helps SREs and engineering teams investigate production incidents faster, identify root causes, and execute remediation with confidence. It combines a React operations dashboard, a FastAPI backend, and a LangGraph multi-agent orchestration layer to deliver a structured, observable incident response experience.

## Live Demo

**Live application:** https://sentinelai-incident-response.vercel.app

> This link is the intended Vercel target. It becomes active once the frontend is deployed successfully and the backend endpoint is configured.

## What This Project Does

SentinelAI provides a complete incident response workflow:

- Accepts incident investigation requests from users.
- Executes autonomous evidence gathering through specialized agents.
- Correlates alerts, logs, metrics, deployments, dependencies, and historical incidents.
- Generates ranked root cause hypotheses and remediation recommendations.
- Produces executive and technical incident reports.
- Supports human approval of remediation before persistence.
- Persists investigation context, audit logs, and reports for future review.

## Industry-Level Architecture

SentinelAI is built using Clean Architecture principles:

- **API layer** (`backend/app/api`): FastAPI endpoints, input validation, response serialization.
- **Application layer** (`backend/app/services`, `backend/app/agents`, `backend/app/graphs`, `backend/app/tools`): orchestration, business use cases, agent execution, tool integration.
- **Domain layer** (`backend/app/domain`): core incident and investigation entities, value objects, enums, and domain rules.
- **Infrastructure layer** (`backend/app/infrastructure`, `backend/app/repositories`): database, caching, vector search, LLM adapters, and datasource providers.
- **Observability** (`backend/app/observability`): LangFuse and OpenTelemetry instrumentation for traceability.

### Core principles

- **Clean layering:** inner business rules do not depend on outer frameworks.
- **Domain-driven modeling:** incident and investigation concepts are expressed as domain objects.
- **Repository pattern:** persistence behind interfaces; database details are replaceable.
- **Dependency injection:** services receive collaborators from configuration.
- **Multi-agent orchestration:** a supervisor graph coordinates agent execution and approval flow.
- **Deployment readiness:** Docker Compose, Vercel support, health checks, and CI workflows.

## System Capabilities

### AI orchestration

- **Supervisor Graph:** orchestrates the flow of agent execution, retries, and approval states.
- **Specialized agents:** alert analysis, log analysis, metrics analysis, deployment analysis, dependency analysis, historical incident search, root cause analysis, recommendation generation, reflection, reporting, and notification drafting.
- **LangChain tools:** reusable tools for log search, metrics query, deployment history, incident search, vector search, SQL execution, markdown/PDF/Word reporting, chart generation, and timeline creation.
- **Typed investigation state:** tracks incident metadata, execution plan, agent outputs, evidence, hypotheses, recommendations, logs, trace IDs, and approval status.

### Backend capabilities

- **FastAPI REST API:** authentication, incidents, investigations, reports, users, health checks.
- **Business services:** application use cases in `backend/app/services/*`.
- **SQL persistence:** PostgreSQL, SQLAlchemy ORM, Alembic migrations.
- **Redis support:** caching, rate limiting, session coordination.
- **Qdrant vector search:** historical incident memory and semantic retrieval.
- **Security:** JWT access + refresh token auth, RBAC roles, request validation, audit logging.
- **Observability:** LangFuse event tracking and OpenTelemetry tracing.

### Frontend capabilities

- **React dashboard:** modern incident operations interface.
- **Main pages:** Login, Dashboard, Incidents, Investigation Detail, Historical Incidents, Settings.
- **Data layer:** React Query and Axios with token refresh handling.
- **UI components:** shared badges, cards, protected routes, and layout.
- **SPA routing:** Vite with client-side routing and fallback support.
- **Deployment-ready:** static build via Vite and Vercel-friendly config.

## File and component map

### Backend

- `backend/app/main.py` — application factory, lifecycle, logging, CORS, and startup behavior.
- `backend/app/config/settings.py` — environment-driven configuration with production validation.
- `backend/app/config/logging.py` — logging setup and structured log output.
- `backend/app/api/v1/routes/` — API routes for authentication, users, incidents, investigations, and health.
- `backend/app/api/deps.py` — dependency injection helpers and authentication dependencies.
- `backend/app/services/` — application service classes implementing business operations.
- `backend/app/agents/` — agent classes for reasoning, analysis, control, and reporting.
- `backend/app/graphs/` — supervisor graph, runner, registry, and node definitions.
- `backend/app/tools/` — tool definitions for reusable LangChain/LLM operations.
- `backend/app/domain/` — entities, value objects, enums, and domain exceptions.
- `backend/app/repositories/` — repository interfaces and concrete SQLAlchemy implementations.
- `backend/app/infrastructure/` — LLM providers, datasource providers, and mock infrastructure.
- `backend/app/state/` — typed investigation state management.
- `backend/app/models/` — SQLAlchemy models for users, incidents, investigations, reports, and audit logs.
- `backend/app/middleware/` — error handling and correlation ID middleware.
- `backend/app/observability/` — LangFuse client and OpenTelemetry tracing setup.
- `backend/app/prompts/` — agent prompt templates and system message definitions.
- `backend/tests/` — unit, integration, graph, API, and agent tests.
- `backend/alembic/` — database migration scripts and environment config.
- `backend/docker-entrypoint.sh` — container startup script with database readiness and migrations.
- `backend/Dockerfile` — backend container image build.

### Frontend

- `frontend/src/main.tsx` — React app bootstrap.
- `frontend/src/App.tsx` — route and page configuration.
- `frontend/src/pages/` — pages for dashboard, incidents, investigation details, historical incidents, login, settings.
- `frontend/src/services/api.ts` — Axios instance, auth header injection, refresh token handling.
- `frontend/src/hooks/queries.ts` — API query hooks using React Query.
- `frontend/src/contexts/AuthContext.tsx` — authentication state and provider.
- `frontend/src/components/ProtectedRoute.tsx` — auth-protected route wrapper.
- `frontend/src/layouts/DashboardLayout.tsx` — shared dashboard layout.
- `frontend/src/components/ui.tsx` — shared UI primitives and badges.
- `frontend/vercel.json` — Vercel static deployment config.
- `frontend/public/_redirects` — redirect support for SPA routing.
- `frontend/Dockerfile` — frontend container build.
- `frontend/tsconfig.json`, `frontend/vite.config.ts` — TypeScript and Vite build config.

## Agents, graphs, and tools

- `backend/app/agents/analysis_agents.py` — evidence-gathering agents for alerts, logs, metrics, deployments, and dependencies.
- `backend/app/agents/reasoning_agents.py` — reasoning agents for root cause, recommendation, and reflection.
- `backend/app/agents/reporting_agents.py` — report generation and notification drafting.
- `backend/app/graphs/supervisor_graph.py` — graph definition and execution order.
- `backend/app/graphs/runner.py` — graph runner and checkpointing.
- `backend/app/graphs/baseline_nodes.py` — base nodes and reusable graph node patterns.
- `backend/app/tools/retrieval_tools.py` — vector and memory retrieval tools.
- `backend/app/tools/report_tools.py` — report generation, chart, and document tools.
- `backend/app/tools/analysis_tools.py` — analysis helpers and prompt-based tool wrappers.
- `backend/app/tools/base.py` — base tool classes and interface definitions.

## Dashboard and frontend experience

The dashboard is built for operational visibility:

- **Dashboard page:** incident counts, active incident summary, awaiting approval stats.
- **Incident list:** quick access to open incidents with severity and status.
- **Investigation details:** investigation state, agent outputs, reports, and approval actions.
- **Historical view:** search and replay past incident investigations.
- **Settings:** configuration and user profile controls.

## Deployment and CI

### Docker Compose

The full stack is orchestrated with `docker-compose.yml`:

- `postgres` — primary relational database.
- `redis` — cache and coordination.
- `qdrant` — vector search store.
- `backend` — FastAPI application.
- `frontend` — static frontend served by Nginx.

### GitHub Actions

- `.github/workflows/ci.yml` — backend lint/test and frontend build validation.
- `.github/workflows/vercel-deploy.yml` — automated frontend deployment to Vercel on `main`.

### Vercel support

- `frontend/vercel.json` — Vercel build config and environment defaults.
- `frontend/public/_redirects` — SPA route fallback for client-side navigation.

## Health, observability, and quality

- `/health` — liveness endpoint.
- `/health/ready` — readiness check against the database.
- LangFuse tracing for LLM calls and agent workflow execution.
- OpenTelemetry for API and backend tracing.
- JSON structured logs and correlation IDs.
- `scripts/quality-check.sh` — local lint and test quality gate.

## Environment Variables

Critical environment variables:

- `APP_ENV`
- `APP_DEBUG`
- `JWT_SECRET_KEY`
- `BOOTSTRAP_ADMIN_EMAIL`
- `BOOTSTRAP_ADMIN_PASSWORD`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL`
- `REDIS_URL`
- `QDRANT_URL`
- `LLM_PROVIDER`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `VITE_API_BASE_URL`

## Suitable industry use cases

- Incident response automation for cloud-native services.
- Post-incident root cause investigation and reporting.
- SRE workflow acceleration and documentation generation.
- Knowledge retention through vectorized incident memory.
- Decision support for remediation approval and stakeholder communication.

## Recommended next steps

1. Wire real data providers for logs, metrics, and deployment history.
2. Add production-grade observability connectors (Loki, Prometheus, Grafana, Sentry).
3. Harden authentication and RBAC rules for multi-tenant operations.
4. Complete the dashboard with timelines, root cause visualizations, and report exports.
5. Configure Vercel with the real backend URL and confirm the first successful deployment.

## License

This project is intended for internal, demonstration, or portfolio use unless otherwise specified by the repository owner.

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
