import logging
import math
from collections import defaultdict
from datetime import timedelta
from sqlalchemy.orm import Session
from models.entities import PriceHistory, TrendSnapshot, WeeklyPrediction
from services.ml_service import train_prediction_model, MODEL_VERSION, VERIFIED_SOURCES

logger = logging.getLogger(__name__)


def calculate_growth_rate(current, previous):
    return (current - previous) / previous if previous > 0 else 0.0


def run_trend_detection(db: Session):
    history = db.query(PriceHistory).order_by(PriceHistory.captured_at.asc()).all()
    groups = defaultdict(list)
    for row in history:
        groups[row.product_id].append(row)
    failed = False
    try:
        predictions = train_prediction_model(db)
    except Exception:
        logger.exception("Weekly model failed; conventional analytics remain available")
        predictions, failed = {}, True
    processed = 0
    for product_id, rows in groups.items():
        latest = rows[-1]
        value = predictions.get(product_id)
        if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
            value = None
        status = "available" if value is not None else (
            "model_error" if failed else "insufficient_data")
        if latest.data_source not in VERIFIED_SOURCES or product_id.startswith("DEMO-"):
            value, status = None, "unverified_data"
        prediction = db.query(WeeklyPrediction).filter_by(
            product_id=product_id, captured_at=latest.captured_at).first()
        if prediction is None:
            prediction = WeeklyPrediction(product_id=product_id, captured_at=latest.captured_at)
            db.add(prediction)
        prediction.predicted_increment = value
        prediction.status = status
        prediction.model_version = MODEL_VERSION
        base = next((r for r in reversed(rows)
                     if r.captured_at <= latest.captured_at - timedelta(days=7)), None)
        growth = calculate_growth_rate(latest.sold_quantity, base.sold_quantity) if base else 0.0
        snapshot = db.query(TrendSnapshot).filter_by(
            product_id=product_id, captured_at=latest.captured_at).first()
        if snapshot is None:
            snapshot = TrendSnapshot(product_id=product_id, captured_at=latest.captured_at)
            db.add(snapshot)
        snapshot.growth_rate = growth
        snapshot.is_trending = growth > .30
        # Legacy numeric column retained for DB compatibility, never used by
        # the predictions API. Availability lives in weekly_predictions.
        snapshot.predicted_sales_next_week = value if value is not None else 0.0
        processed += 1
    db.commit()
    return processed
