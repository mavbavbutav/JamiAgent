#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID=""
REGION="us-central1"
REPO="jami-agent"
SERVICE="jami-agent-api"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT_ID="$2"; shift 2 ;;
    --region) REGION="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --service) SERVICE="$2"; shift 2 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

if [[ -z "$PROJECT_ID" ]]; then
  echo "--project is required"
  exit 1
fi

IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/api:$(date +%Y%m%d-%H%M%S)"

echo "Building image: ${IMAGE}"
gcloud builds submit apps/api --tag "${IMAGE}" --project "${PROJECT_ID}"

echo "Deploying service: ${SERVICE}"
gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production,DEBUG=false

echo "Done."
