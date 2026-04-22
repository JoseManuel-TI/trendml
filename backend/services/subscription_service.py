from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from models.entities import CheckoutAttempt, User
from services.email_service import send_checkout_reminder_email


def create_checkout_attempt(
    db: Session,
    *, 
    user_id: int,
    plan: str,
    provider: str,
    preference_id: Optional[str],
    checkout_url: Optional[str],
):
    attempt = CheckoutAttempt(
        user_id=user_id,
        plan=plan,
        provider=provider,
        preference_id=preference_id,
        checkout_url=checkout_url,
        status="pending",
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def mark_checkout_approved(db: Session, *, user_id: int, plan: str):
    attempt = (
        db.query(CheckoutAttempt)
        .filter(
            CheckoutAttempt.user_id == user_id,
            CheckoutAttempt.plan == plan,
            CheckoutAttempt.status == "pending",
        )
        .order_by(CheckoutAttempt.created_at.desc())
        .first()
    )
    if attempt:
        attempt.status = "approved"
        db.add(attempt)
        db.commit()


def process_abandoned_checkout_reminders(db: Session) -> dict:
    threshold = datetime.utcnow() - timedelta(hours=24)
    pending_attempts = (
        db.query(CheckoutAttempt)
        .filter(
            CheckoutAttempt.status == "pending",
            CheckoutAttempt.created_at <= threshold,
            CheckoutAttempt.reminder_sent_at.is_(None),
        )
        .order_by(CheckoutAttempt.created_at.asc())
        .limit(200)
        .all()
    )

    sent = 0
    for attempt in pending_attempts:
        user = db.query(User).filter(User.id == attempt.user_id, User.is_active.is_(True)).first()
        if not user:
            continue
        if not attempt.checkout_url:
            continue

        ok = send_checkout_reminder_email(user.email, attempt.plan, attempt.checkout_url)
        if ok:
            attempt.reminder_sent_at = datetime.utcnow()
            db.add(attempt)
            sent += 1

    db.commit()
    return {"pending_found": len(pending_attempts), "reminders_sent": sent}
