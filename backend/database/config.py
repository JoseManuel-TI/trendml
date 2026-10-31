from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    academic_mode: bool = os.getenv("ACADEMIC_MODE", "true").lower() == "true"
    admin_emails: str = os.getenv("ADMIN_EMAILS", "")
    app_name: str = os.getenv("APP_NAME", "TrendML API")
    app_env: str = os.getenv("APP_ENV", "development")
    app_secret: str = os.getenv("APP_SECRET", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://trendml:trendml@postgres:5432/trendml",
    )
    ml_site: str = os.getenv("ML_SITE", "MLA")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    backend_public_url: str = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")
    mercadopago_access_token: str = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
    mercadopago_webhook_secret: str = os.getenv("MERCADOPAGO_WEBHOOK_SECRET", "")
    email_provider: str = os.getenv("EMAIL_PROVIDER", "console")
    email_from: str = os.getenv("EMAIL_FROM", "TrendML <noreply@trendml.app>")
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    internal_cron_token: str = os.getenv("INTERNAL_CRON_TOKEN", "dev-internal-token")
    ml_client_id: str = os.getenv("ML_CLIENT_ID", "")
    ml_client_secret: str = os.getenv("ML_CLIENT_SECRET", "")


settings = Settings()
