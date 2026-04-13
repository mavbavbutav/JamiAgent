# Deployment Guide (Fast Path to Cloud Run)

This guide is optimized for shipping Jami Agent quickly with guardrails.

## 1) Pre-flight checklist

- Verify OpenAI API key, model, and base URL for live Responses API calls.
- Create Cloud SQL Postgres instance.
- Store all runtime secrets in Secret Manager.
- Set `ENVIRONMENT=production` and `DEBUG=false`.

## 2) Required services

Enable in your GCP project:

- Cloud Run
- Cloud Build
- Artifact Registry
- Secret Manager
- Cloud SQL Admin API

## 3) Build + deploy

Use the helper script from repo root:

```bash
./scripts/deploy_cloud_run.sh \
  --project PROJECT_ID \
  --region us-central1 \
  --repo jami-agent \
  --service jami-agent-api
```

The script will:

1. Build and push a container image to Artifact Registry.
2. Deploy Cloud Run service revision with `ENVIRONMENT=production` and `DEBUG=false`.
3. Require runtime secrets to be wired from Secret Manager.

## 4) Smoke test

```bash
./scripts/smoke_test.sh https://YOUR_CLOUD_RUN_URL
```

Checks:

- `/health`
- `/ready`
- `/version`

## 5) Rollout recommendation

- Deploy with `--no-traffic` for first revision.
- Run smoke test.
- Shift traffic gradually (5%, 25%, 100%).
- Keep previous revision for instant rollback.
