from __future__ import annotations

import hmac
import hashlib
from dataclasses import dataclass
from typing import Optional, Tuple

import requests

from database.config import settings


PLAN_CATALOG = {
    "starter": {"name": "TrendML Starter", "price_ars": 9000},
    "pro": {"name": "TrendML Pro", "price_ars": 29000},
    "premium": {"name": "TrendML Premium", "price_ars": 59000},
}


@dataclass
class CheckoutResult:
    checkout_url: str
    preference_id: str


def is_configured() -> bool:
    return bool(settings.mercadopago_access_token)


def create_preference(plan: str, user_id: int, user_email: str) -> CheckoutResult:
    if plan not in PLAN_CATALOG:
        raise ValueError("invalid plan")
    if not settings.mercadopago_access_token:
        raise RuntimeError("Mercado Pago not configured")

    item = PLAN_CATALOG[plan]
    payload = {
        "items": [
            {
                "title": item["name"],
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(item["price_ars"]),
            }
        ],
        "external_reference": f"trendml:user:{user_id}:plan:{plan}",
        "payer": {"email": user_email},
        "back_urls": {
            "success": f"{settings.frontend_url}/dashboard?billing=success",
            "failure": f"{settings.frontend_url}/pricing?billing=failure",
            "pending": f"{settings.frontend_url}/pricing?billing=pending",
        },
        "auto_return": "approved",
        "notification_url": f"{settings.backend_public_url}/api/subscriptions/webhook/mercadopago",
        "metadata": {"user_id": user_id, "plan": plan},
    }

    response = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers={
            "Authorization": f"Bearer {settings.mercadopago_access_token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    return CheckoutResult(
        checkout_url=data.get("init_point", ""),
        preference_id=data.get("id", ""),
    )


def get_payment(payment_id: str) -> dict:
    response = requests.get(
        f"https://api.mercadopago.com/v1/payments/{payment_id}",
        headers={"Authorization": f"Bearer {settings.mercadopago_access_token}"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def parse_external_reference(external_reference: str) -> Tuple[Optional[int], Optional[str]]:
    # trendml:user:12:plan:pro
    try:
        parts = external_reference.split(":")
        user_id = int(parts[2])
        plan = parts[4]
        if plan not in PLAN_CATALOG:
            return None, None
        return user_id, plan
    except (IndexError, ValueError):
        return None, None


def verify_webhook_signature(x_signature: str, data_id: str, x_request_id: str) -> bool:
    if not settings.mercadopago_webhook_secret:
        return True

    if not x_signature:
        return False

    ts = ""
    v1 = ""
    for part in x_signature.split(","):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        if key.strip() == "ts":
            ts = value.strip()
        if key.strip() == "v1":
            v1 = value.strip()

    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
    digest = hmac.new(
        settings.mercadopago_webhook_secret.encode(),
        msg=manifest.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(digest, v1)
