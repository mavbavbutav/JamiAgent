# Architecture Overview

This document provides a high‑level overview of the architecture for the cloud‑based professional assistant. It is derived from the blueprint discussed in previous conversations and refined to prioritise innovation, efficiency and operational discipline.

## Components

### Frontend

The frontend is a single‑page application hosted separately from the backend API. It provides a chat interface, approval queue, document upload UI and conversation history. It authenticates the user via OAuth (Google or Microsoft) and sends authenticated requests to the backend.

### API Service

The API service is implemented using FastAPI and is deployed on Google Cloud Run. It serves as the entry point for client requests and orchestrates interactions between the user, the OpenAI model and external services. Key responsibilities include:

- **Authentication and Authorisation** – verifying user identity and enforcing role‑based access control.
- **Conversation Management** – maintaining chat state across turns using the OpenAI Conversations API and storing metadata in PostgreSQL.
- **Tool Invocation** – exposing a set of well‑defined tools (calendar, email drafting, knowledge search, etc.) to the model via function calling. Tool calls requiring side effects (e.g. sending an email) are intercepted and stored as pending approvals.
- **Knowledge Retrieval** – using OpenAI’s file search and vector stores to provide retrieval‑augmented generation based on uploaded documents.
- **Approval Workflow** – storing and presenting pending actions for user review and executing them only upon approval.
- **Audit Logging** – recording all user inputs, model outputs, tool invocations, approvals and errors in the database for compliance and debugging.
- **Background Jobs** – dispatching long‑running tasks (e.g. weekly report generation, nightly indexing) to Cloud Run Jobs or similar asynchronous workers.

### Database

A PostgreSQL database hosted on Cloud SQL acts as the source of truth for application state. Tables include users, conversations, messages, tool calls, approvals, documents, tasks and audit logs. A database connection pool is used to manage connections efficiently in the serverless environment. Managed connection pooling or an external proxy (such as Cloud SQL Auth Proxy) is recommended.

### Knowledge Base

Document ingestion is handled via the OpenAI file batch API. Uploaded files are converted into vector embeddings and stored in vector stores. Each document is tagged with metadata (scope, owner, type, tags) to allow fine‑grained filtering. Retrieval calls from the model should respect these metadata constraints. Documents are grouped into evergreen, recent operational and project‑specific stores with appropriate expiration policies.

### Secrets

Secrets such as API keys, database credentials and OAuth client secrets are stored in Google Cloud Secret Manager. The runtime fetches them at startup via environment variables injected through Cloud Run. Secrets should not be committed to version control.

### Observability

The application emits structured logs for every request, model call and tool invocation. Google Cloud Monitoring captures CPU, memory and request metrics. Error tracking and alerting are configured to notify the operations team. Latency budgets are defined for interactive and background workflows and enforced via request timeouts and health checks.

## Deployment

The API service is containerised using the provided `Dockerfile` and deployed via Cloud Run. A CI/CD pipeline builds and tests each revision, pushes it to Artifact Registry and deploys it to Cloud Run. Traffic splitting and automatic rollbacks are used to manage releases. Cloud Run Jobs are used for scheduled tasks such as nightly indexing and evaluation harness runs.

## Further Reading

Refer to `prompts.md` for details on prompt layering and caching, and `tool-contracts.md` for precise tool schemas. The runbooks (`runbooks.md`) describe operational procedures, incident response and maintenance tasks.