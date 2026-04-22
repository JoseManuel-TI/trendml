from collections import defaultdict
from datetime import datetime
from sqlalchemy.orm import Session

from models.entities import PriceHistory, TrendSnapshot
from services.ml_service import train_prediction_model


def calculate_growth_rate(current: int, previous: int) -> float:
    if previous <= 0:
        return 0.0
    return (current - previous) / previous


def run_trend_detection(db: Session) -> int:
    price_history = db.query(PriceHistory).order_by(PriceHistory.captured_at.asc()).all()
    by_product = defaultdict(list)
    for row in price_history:
        by_product[row.product_id].append(row)

    predictions = train_prediction_model(db)
    inserted = 0

    for product_id, rows in by_product.items():
        if len(rows) < 2:
            continue
        latest = rows[-1]
        one_week_ago = rows[-8] if len(rows) > 8 else rows[0]

        growth_rate = calculate_growth_rate(latest.sold_quantity, one_week_ago.sold_quantity)
        snapshot = TrendSnapshot(
            product_id=product_id,
            growth_rate=growth_rate,
            predicted_sales_next_week=predictions.get(product_id, float(latest.sold_quantity)),
            is_trending=growth_rate > 0.30,
            captured_at=latest.captured_at if latest.captured_at else datetime.utcnow(),
        )
        db.add(snapshot)
        inserted += 1

    db.commit()
    return inserted
