# TrendML

TrendML es un SaaS MVP de inteligencia de mercado para vendedores de Mercado Libre.

Incluye:
- Backend en FastAPI con JWT
- Worker de recolección de datos desde API pública de Mercado Libre
- Motor de tendencias y predicciones simples con scikit-learn
- Frontend Next.js con landing + pricing + dashboard
- Checkout con Mercado Pago + webhook de activación de plan
- Feature gating por suscripción (`starter`, `pro`, `premium`)
- Docker Compose con `frontend`, `backend`, `postgres`, `worker`

## Estructura

- `backend/`: API, auth, pagos, modelos y analytics
- `frontend/`: landing, pricing, login/register y dashboard
- `worker/`: colector de datos y detector de tendencias
- `docker/`: Dockerfiles

## Variables de entorno

Copia `.env.example` a `.env` y ajusta:

- `APP_SECRET`
- `DATABASE_URL` (local recomendado: `sqlite:///./trendml.db`)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` (solo si usas Docker/PostgreSQL)
- `ML_SITE`
- `ML_QUERIES`
- `NEXT_PUBLIC_API_URL`
- `FRONTEND_URL`
- `BACKEND_PUBLIC_URL`
- `MERCADOPAGO_ACCESS_TOKEN`
- `MERCADOPAGO_WEBHOOK_SECRET` (opcional, recomendado)
- `EMAIL_PROVIDER` (`console`, `resend`, `smtp`)
- `EMAIL_FROM`
- `RESEND_API_KEY` (si usas `resend`)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_USE_TLS` (si usas `smtp`)
- `INTERNAL_CRON_TOKEN` (token para jobs internos)
- `BACKEND_INTERNAL_URL` (URL interna del backend para worker)

## Ejecutar sin Docker (recomendado)

### 1) Setup inicial

```bash
bash scripts/setup_local.sh
```

### 2) Levantar backend

En una terminal:

```bash
bash scripts/run_backend.sh
```

### 3) Levantar frontend

En otra terminal:

```bash
bash scripts/run_frontend.sh
```

### 4) Cargar datos demo

En otra terminal:

```bash
bash scripts/seed_local.sh
```

Luego entra en `http://localhost:3000/login` y usa el botón `Entrar como demo`.

App:
- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

### Opción rápida: levantar todo con 1 comando

Después del setup inicial:

```bash
bash scripts/start_all_local.sh
```

Esto inicia backend + frontend juntos. Para detener ambos: `Ctrl+C`.

### Worker manual local (opcional)

```bash
bash scripts/run_worker_local.sh
```

## Ejecutar con Docker (opcional)

```bash
docker compose up --build
```

Servicios:
- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

## Flujo comercial

1. Usuario se registra en `/register`.
2. En `/pricing` elige plan y se redirige a Mercado Pago.
3. Mercado Pago llama al webhook `POST /api/subscriptions/webhook/mercadopago`.
4. Si el pago está `approved`, se activa el plan del usuario.
5. El dashboard desbloquea features según plan.
6. Se disparan emails automáticos:
   - bienvenida (registro),
   - recuperación de checkout (inicio de pago),
   - confirmación de plan activo (pago aprobado).

## Gating de planes

- `starter`: acceso a `GET /api/trending`
- `pro`: además `GET /api/price-alerts` y `GET /api/predictions`
- `premium`: además `GET /api/top-sellers`, `GET /api/admin/metrics` y `GET /api/admin/funnel`
  - `GET /api/admin/pending-leads` para cierre manual de pagos pendientes

## Endpoints de suscripción

- `GET /api/subscriptions/plans`
- `POST /api/subscriptions/checkout`
- `POST /api/subscriptions/webhook/mercadopago`

Si `MERCADOPAGO_ACCESS_TOKEN` no está configurado, `checkout` funciona en modo `mock` para pruebas.

## Automatización de emails

- `EMAIL_PROVIDER=console`: imprime emails en logs (dev).
- `EMAIL_PROVIDER=resend`: usa API de Resend (`RESEND_API_KEY`).
- `EMAIL_PROVIDER=smtp`: usa servidor SMTP estándar.

Eventos implementados:
- `register`: email de bienvenida.
- `checkout`: email para recuperar compra no finalizada.
- `webhook approved`: email de pago aprobado.

## Recuperación automática (24h)

TrendML guarda intentos de checkout y ejecuta cada hora un job interno:
- detecta checkouts `pending` con más de 24h,
- envía recordatorio por email con link de pago,
- marca el recordatorio para no reenviar.

Endpoint interno:
- `POST /api/internal/checkout-reminders` (requiere header `x-internal-token`).

## Seed comercial (demo inmediata)

Para ver dashboard comercial con datos desde el primer día:

```bash
cd backend
python -m scripts.seed_commercial
```

Esto crea:
- usuarios demo,
- checkouts aprobados/pending,
- funnel de ingresos,
- leads pendientes para cierre manual,
- productos/price history/trends para analytics.

## WhatsApp de cierre manual

El bloque `Leads Pendientes` incluye botón de WhatsApp directo al cliente.
Para eso, el teléfono se captura en `/register` (campo WhatsApp).

Formato recomendado para registro:
- código país sin `+` (ejemplo Argentina móvil: `54911...`).

## Desarrollo local sin Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Worker manual

```bash
python worker/data_collector.py
python worker/trend_detector.py
```

## Lanzamiento rápido (48h)

1. Configura Mercado Pago (`MERCADOPAGO_ACCESS_TOKEN`) y prueba un cobro real de bajo monto.
2. Publica landing + pricing y abre canal de ventas (WhatsApp/LinkedIn).
3. Ofrece plan Pro con onboarding manual a primeros 10 clientes.
4. Recolecta feedback y ajusta consultas/categorías de mayor demanda.
