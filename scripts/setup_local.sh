#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/4] Configurando .env local..."
if [ ! -f .env ]; then
  cat > .env << 'ENVEOF'
APP_SECRET=dev-secret-change-me
APP_ENV=development
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
DATABASE_URL=sqlite:///./trendml.db
ML_SITE=MLA
ML_QUERIES=notebook,auriculares,mouse gamer
NEXT_PUBLIC_API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
BACKEND_PUBLIC_URL=http://localhost:8000
MERCADOPAGO_ACCESS_TOKEN=
MERCADOPAGO_WEBHOOK_SECRET=
EMAIL_PROVIDER=console
EMAIL_FROM=TrendML <noreply@trendml.app>
RESEND_API_KEY=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_USE_TLS=true
INTERNAL_CRON_TOKEN=dev-internal-token
BACKEND_INTERNAL_URL=http://localhost:8000
ENVEOF
  echo "Archivo .env creado."
else
  echo "Archivo .env ya existe, no se sobrescribe."
fi

echo "[2/4] Instalando backend..."
cd "$ROOT_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "[3/4] Instalando frontend..."
cd "$ROOT_DIR/frontend"
npm install

echo "[4/4] Setup listo."
echo "Ahora ejecuta:"
echo "  bash scripts/run_backend.sh"
echo "  bash scripts/run_frontend.sh"
echo "  bash scripts/seed_local.sh"
