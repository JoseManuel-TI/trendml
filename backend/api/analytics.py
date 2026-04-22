from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.deps import get_current_user, require_plan
from database.session import get_db
from models.entities import User
from models.schemas import PredictionItem, PriceAlertItem, TopSellerItem, TrendingItem
from services.analytics_service import (
    get_admin_funnel,
    get_admin_metrics,
    get_pending_checkout_leads,
    get_predictions,
    get_price_alerts,
    get_top_sellers,
    get_trending_products,
)

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/trending", response_model=list[TrendingItem])
def trending(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_trending_products(db)


@router.get("/price-alerts", response_model=list[PriceAlertItem])
def price_alerts(_: User = Depends(require_plan("pro", "premium")), db: Session = Depends(get_db)):
    return get_price_alerts(db)


@router.get("/predictions", response_model=list[PredictionItem])
def predictions(_: User = Depends(require_plan("pro", "premium")), db: Session = Depends(get_db)):
    return get_predictions(db)


@router.get("/top-sellers", response_model=list[TopSellerItem])
def top_sellers(_: User = Depends(require_plan("premium")), db: Session = Depends(get_db)):
    return get_top_sellers(db)


@router.get("/admin/metrics")
def admin_metrics(_: User = Depends(require_plan("premium")), db: Session = Depends(get_db)):
    return get_admin_metrics(db)


@router.get("/admin/funnel")
def admin_funnel(_: User = Depends(require_plan("premium")), db: Session = Depends(get_db)):
    return get_admin_funnel(db)


@router.get("/admin/pending-leads")
def admin_pending_leads(_: User = Depends(require_plan("premium")), db: Session = Depends(get_db)):
    return get_pending_checkout_leads(db)
