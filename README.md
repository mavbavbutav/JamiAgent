# Jami Agent

A production-minded starter for building a **professional assistant** on:

- FastAPI backend
- OpenAI Responses/Conversations-oriented orchestration layer
- Tool registry + approval gate pattern
- SQL-backed persistence for conversations, messages, approvals, and audit events
- Cloud Run deployment scaffolding

## Implemented Starter Scope

### API endpoints
- `GET /health`
- `GET /ready`
- `GET /version`
- `POST /chat/send`
- `GET /conversations`
- `POST /conversations`
- `GET /conversations/{id}/messages`
- `GET /approvals`
- `POST /approvals/{id}/approve`
- `POST /approvals/{id}/deny`
- `GET /files`
- `POST /files/upload`
- `POST /files/index`

### Backend architecture in code
- `AssistantOrchestrator` with basic function-calling loop (tool execution + follow-up response)
- `OpenAIClientService` with Responses API integration + local fallback mode
- `ToolRegistryService` with level-based tool metadata
- `ApprovalService` backed by SQLAlchemy
- `ConversationService` for conversation/message persistence
- `AuditService` for DB-backed event logs
- SQLAlchemy models for `conversations`, `messages`, `approvals`, and `audit_log`
- DB bootstrap on startup to initialize tables

## Quickstart

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for Swagger UI.

## Deployment

- Cloud Run service template: `infra/cloudrun/service.yaml`
- Cloud Run job template: `infra/cloudrun/job.yaml`
- Fast-path deployment guide: `docs/deployment.md`
- Deploy script: `scripts/deploy_cloud_run.sh`
- Smoke test script: `scripts/smoke_test.sh`

## Current Gaps Before Production

1. Persist and reconcile OpenAI conversation/response IDs for robust resume semantics across sessions.
2. Implement auth/SSO and RBAC middleware.
3. Add durable models/migrations for users, tool calls, tasks, and prompt version tracking.
4. Implement files ingestion/indexing and retrieval-backed answering.
5. Add integration/unit tests and CI policy checks.
6. Add metrics, tracing, and alerting for runtime operations.
