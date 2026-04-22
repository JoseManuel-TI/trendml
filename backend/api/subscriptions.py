from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from database.session import get_db
from models.entities import User
from payments.mercadopago_service import (
    PLAN_CATALOG,
    create_preference,
    get_payment,
    is_configured,
    parse_external_reference,
    verify_webhook_signature,
)
from services.email_service import send_checkout_started_email, send_payment_approved_email
from services.subscription_service import create_checkout_attempt, mark_checkout_approved

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

ALLOWED_PLANS = {"starter", "pro", "premium"}


class UpdatePlanRequest(BaseModel):
    plan: str


@router.get("/plans")
def plans():
    return {
        "plans": [
            {"id": "starter", "price_ars": PLAN_CATALOG["starter"]["price_ars"]},
            {"id": "pro", "price_ars": PLAN_CATALOG["pro"]["price_ars"]},
            {"id": "premium", "price_ars": PLAN_CATALOG["premium"]["price_ars"]},
        ],
        "provider": "mercadopago" if is_configured() else "mock",
    }


@router.post("/checkout")
def checkout(payload: UpdatePlanRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.plan not in ALLOWED_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    if not is_configured():
        user.subscription_plan = payload.plan
        db.add(user)
        db.commit()
        create_checkout_attempt(
            db,
            user_id=user.id,
            plan=payload.plan,
            provider="mock",
            preference_id=None,
            checkout_url=None,
        )
        return {
            "status": "active",
            "plan": payload.plan,
            "provider": "mock",
            "checkout_url": None,
            "message": "Mercado Pago no configurado: activación simulada para desarrollo.",
        }

    preference = create_preference(payload.plan, user.id, user.email)
    create_checkout_attempt(
        db,
        user_id=user.id,
        plan=payload.plan,
        provider="mercadopago",
        preference_id=preference.preference_id,
        checkout_url=preference.checkout_url,
    )
    if preference.checkout_url:
        send_checkout_started_email(user.email, payload.plan, preference.checkout_url)
    return {
        "status": "pending",
        "plan": payload.plan,
        "provider": "mercadopago",
        "checkout_url": preference.checkout_url,
        "preference_id": preference.preference_id,
    }


@router.post("/webhook/mercadopago")
async def mercadopago_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: str = Header(default="", alias="x-signature"),
    x_request_id: str = Header(default="", alias="x-request-id"),
):
    payload = {}
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    payment_id = str(data.get("id", "") or request.query_params.get("data.id", "") or request.query_params.get("id", ""))

    if not payment_id:
        return {"ok": True, "ignored": "missing payment id"}

    if not verify_webhook_signature(x_signature, payment_id, x_request_id):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payment = get_payment(payment_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error fetching payment: {exc}") from exc

    if payment.get("status") != "approved":
        return {"ok": True, "ignored": f"payment status: {payment.get('status')}"}

    user_id, plan = parse_external_reference(payment.get("external_reference", ""))
    if not user_id or not plan:
        return {"ok": True, "ignored": "invalid external reference"}

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"ok": True, "ignored": "user not found"}

    user.subscription_plan = plan
    db.add(user)
    db.commit()
    mark_checkout_approved(db, user_id=user_id, plan=plan)
    send_payment_approved_email(user.email, plan)

    return {"ok": True, "user_id": user_id, "plan": plan, "status": "activated"}
