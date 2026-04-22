from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from database.config import settings
from database.session import get_db
from services.subscription_service import process_abandoned_checkout_reminders

router = APIRouter(prefix="/api/internal", tags=["internal"])


@router.post("/checkout-reminders")
def checkout_reminders(
    db: Session = Depends(get_db),
    x_internal_token: str = Header(default="", alias="x-internal-token"),
):
    if x_internal_token != settings.internal_cron_token:
        raise HTTPException(status_code=401, detail="Invalid internal token")

    return process_abandoned_checkout_reminders(db)
