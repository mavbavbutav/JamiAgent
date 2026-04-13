# Operational Runbooks

This document is a placeholder for operational runbooks. Fill in procedures for deploying updates, rotating secrets, handling incidents, and performing database migrations.

## Deployment

- Use the CI/CD pipeline to build and deploy the container. Validate changes in staging before promoting to production using Cloud Run’s traffic splitting.
- Rollbacks can be performed by reverting the Cloud Run revision or via the CI pipeline.
- Always update the `service.yaml` with the correct image tag for production deployments.

## Secret Rotation

- Store secrets in Google Cloud Secret Manager and reference them in the Cloud Run service configuration.
- Rotate API keys and credentials regularly. After rotating, update the secret values in Secret Manager and redeploy the Cloud Run service.

## Incident Response

- Investigate logs in Cloud Logging for errors or unusual behaviour.
- Use the audit log table to trace actions leading up to incidents.
- If the assistant sends an unauthorised message, immediately disable the relevant tool and revoke credentials.

## Database Migrations

- Use a migration tool such as Alembic or SQLAlchemy migrations to apply schema changes.
- Migrations should be executed before deploying code that depends on the new schema.

For more detailed procedures, expand this document as the system matures.