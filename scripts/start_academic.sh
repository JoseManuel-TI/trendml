#!/bin/bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export DATABASE_URL="sqlite:///$ROOT_DIR/work/academic.db"
export ACADEMIC_MODE=true
export EMAIL_PROVIDER=console
export APP_ENV=development
export PYTHONPATH="$ROOT_DIR/backend"
mkdir -p work
if [ ! -x backend/.venv/bin/python ]; then
  echo 'Primero ejecuta: bash scripts/setup_local.sh'; exit 1
fi
for port in 8000 3000; do
  if lsof -tiTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "El puerto $port está ocupado. Detén la instancia anterior antes de iniciar esta demo."; exit 1
  fi
done
backend/.venv/bin/python scripts/seed_academic.py
backend/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
(cd frontend && npm run dev -- --hostname 127.0.0.1) &
FRONTEND_PID=$!
trap 'kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true' EXIT
trap 'exit 0' INT TERM
printf 'Abre http://localhost:3000/login y pulsa Entrar como demo.\n'
wait
