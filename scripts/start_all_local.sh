#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cleanup() {
  echo "\nDeteniendo servicios..."
  if [ -n "$BACKEND_PID" ]; then kill "$BACKEND_PID" 2>/dev/null || true; fi
  if [ -n "$FRONTEND_PID" ]; then kill "$FRONTEND_PID" 2>/dev/null || true; fi
}

trap cleanup EXIT INT TERM

cd "$ROOT_DIR"

if [ ! -d "$ROOT_DIR/backend/.venv" ] || [ ! -f "$ROOT_DIR/.env" ]; then
  echo "Entorno no inicializado. Ejecutando setup automático..."
  bash "$ROOT_DIR/scripts/setup_local.sh"
fi

echo "Iniciando backend en http://localhost:8000 ..."
("$ROOT_DIR/scripts/run_backend.sh") &
BACKEND_PID=$!

sleep 2

echo "Iniciando frontend en http://localhost:3000 ..."
("$ROOT_DIR/scripts/run_frontend.sh") &
FRONTEND_PID=$!

echo "Servicios en ejecución."
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000/docs"
echo "Presiona Ctrl+C para detener todo."

wait "$BACKEND_PID" "$FRONTEND_PID"
