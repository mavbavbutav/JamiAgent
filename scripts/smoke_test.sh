#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-}"
if [[ -z "$BASE_URL" ]]; then
  echo "Usage: $0 https://SERVICE-URL"
  exit 1
fi

curl -fsS "${BASE_URL}/health" >/dev/null
curl -fsS "${BASE_URL}/ready" >/dev/null
curl -fsS "${BASE_URL}/version" >/dev/null

echo "Smoke test passed for ${BASE_URL}"
