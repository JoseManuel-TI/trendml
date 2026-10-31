from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.migrations import ensure_schema

from api.analytics import router as analytics_router
from api.auth import router as auth_router
from api.internal import router as internal_router
from api.subscriptions import router as subscriptions_router
from database.config import settings
from database.session import engine

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    ensure_schema(engine)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}


app.include_router(auth_router)
app.include_router(analytics_router)
app.include_router(subscriptions_router)
app.include_router(internal_router)

from api.forecast import router as forecast_router
app.include_router(forecast_router)
