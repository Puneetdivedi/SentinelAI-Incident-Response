# SentinelAI

SentinelAI is an AI-powered incident response platform with a FastAPI backend and a React frontend.

## Run locally

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Start the full stack with Docker Compose:
   ```bash
   docker compose up --build -d
   ```
3. Open the UI at http://localhost:5173 and the API at http://localhost:8000/health.

## Production-style deployment

The repository is configured for a hosted deployment using Docker Compose on a VPS or cloud VM.

### Recommended flow

1. Fill in the values in .env for your host.
2. Start the stack with:
   ```bash
   ./scripts/deploy.sh
   ```
3. Verify the services:
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   ```

### Important environment variables

- JWT_SECRET_KEY: a strong secret for signing tokens.
- BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD: initial admin credentials.
- APP_ENV=production and APP_DEBUG=false for hosted deployments.

## Project structure

- backend/: FastAPI application and services
- frontend/: React + Vite UI
- docker-compose.yml: orchestrates PostgreSQL, Redis, Qdrant, backend, and frontend

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
