from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api.analytics import router as analytics_router
from api.auth import router as auth_router
from api.internal import router as internal_router
from api.subscriptions import router as subscriptions_router
from database.config import settings
from database.session import engine
from models.base import Base

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        # SQLite may not support "ADD COLUMN IF NOT EXISTS" depending on version.
        # Try generic statement first, then fallback to manual column check.
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(30);"))
        except Exception:
            cols = conn.execute(text("PRAGMA table_info(users);")).fetchall()
            col_names = {row[1] for row in cols} if cols else set()
            if "phone" not in col_names:
                conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(30);"))


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}


app.include_router(auth_router)
app.include_router(analytics_router)
app.include_router(subscriptions_router)
app.include_router(internal_router)
