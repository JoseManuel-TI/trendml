#!/bin/sh
set -e

while true; do
  echo "[worker] collecting data..."
  python /app/worker/data_collector.py || true

  echo "[worker] processing trends..."
  python /app/worker/trend_detector.py || true

  echo "[worker] processing abandoned checkouts..."
  if [ -n "$BACKEND_INTERNAL_URL" ] && [ -n "$INTERNAL_CRON_TOKEN" ]; then
    python - << 'PY'
import os
import requests

url = os.getenv("BACKEND_INTERNAL_URL", "").rstrip("/") + "/api/internal/checkout-reminders"
token = os.getenv("INTERNAL_CRON_TOKEN", "")
if url and token:
    try:
        res = requests.post(url, headers={"x-internal-token": token}, timeout=20)
        print(f"[worker] checkout-reminders status={res.status_code} body={res.text[:300]}")
    except Exception as exc:
        print(f"[worker] checkout-reminders error={exc}")
PY
  else
    echo "[worker] internal reminder job skipped (missing BACKEND_INTERNAL_URL or INTERNAL_CRON_TOKEN)"
  fi

  echo "[worker] sleeping for 1 hour..."
  sleep 3600
done
