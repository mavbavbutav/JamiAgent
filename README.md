# Professional Assistant (Blueprint Implementation)

This repository provides a skeleton implementation of the cloud‑based professional assistant described in the blueprint. It is designed to be deployed on Google Cloud Run and leverages the OpenAI Responses API, Conversations API, structured outputs and file search for stateful reasoning and document retrieval. It includes placeholders for FastAPI endpoints, tool definitions, database models, and infrastructure configuration. Use this as a starting point to build your own assistant with approval workflows and retrieval‑augmented answers.

## Repository Layout

- **apps/web** – a placeholder for the front‑end application. No implementation is provided, but you can drop in a React or Next.js project here.
- **apps/api** – the backend service powering your assistant. It uses FastAPI and contains all the business logic, tool wrappers, routing and agent orchestration.
  - `app/main.py` – entrypoint for the FastAPI app with a minimal chat endpoint and health check.
  - `app/config.py` – environment variable configuration using Pydantic settings.
  - `app/agents/` – place your agent orchestration logic here.
  - `app/routes/` – HTTP route definitions.
  - `app/tools/` – wrappers around external systems (e.g. calendar, email, document search) with strict schemas.
  - `app/db/` – SQLAlchemy models and database utilities.
  - `app/prompts/` – system, tool and user prompts to configure model behaviour.
  - `app/schemas/` – pydantic schemas for request/response bodies and structured outputs.
  - `app/services/` – helper services (OpenAI client, knowledge base manager, approval workflow manager, etc.).
  - `app/middleware/` – middleware for logging, authentication and error handling.
  - `requirements.txt` – Python dependencies for the API service.
  - `Dockerfile` – a container definition for deploying to Cloud Run.
- **infra/cloudrun** – Cloud Run service and job YAML files. These provide placeholders for you to customise service configuration, environment variables, secrets and IAM settings.
- **docs** – additional documentation. `architecture.md` summarises the high‑level design. `prompts.md` outlines prompt layers and policy, while `tool-contracts.md` documents the interface contracts for each tool. `runbooks.md` is a place to add operational runbooks.

## Quickstart

1. Install dependencies (preferably in a virtual environment):
   ```bash
   cd apps/api
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set environment variables based on `.env.example` or configure a `.env` file. At minimum, you will need your OpenAI API key and database connection string.

3. Run the API locally:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Navigate to `http://localhost:8000/docs` to explore the automatically generated interactive API docs.

This is only a skeleton. You must implement the specific tools, database models, knowledge‑base integration and agent logic described in the blueprint to create a production‑ready assistant.
