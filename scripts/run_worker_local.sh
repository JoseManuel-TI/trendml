#!/bin/bash
set -e
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
while IFS= read -r line || [ -n "$line" ]; do
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  key="${line%%=*}"
  value="${line#*=}"
  export "$key=$value"
done < "$ROOT_DIR/.env"
python3 worker/data_collector.py
python3 worker/trend_detector.py
python3 - << 'PY'
import os
import requests
url = os.getenv("BACKEND_INTERNAL_URL", "http://localhost:8000").rstrip("/") + "/api/internal/checkout-reminders"
token = os.getenv("INTERNAL_CRON_TOKEN", "")
if token:
    r = requests.post(url, headers={"x-internal-token": token}, timeout=20)
    print("[worker-local] reminders:", r.status_code, r.text[:300])
else:
    print("[worker-local] INTERNAL_CRON_TOKEN missing, reminders skipped")
PY
