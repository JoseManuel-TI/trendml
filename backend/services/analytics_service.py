from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.entities import CheckoutAttempt, PriceHistory, Product, TrendSnapshot, User, WeeklyPrediction
from payments.mercadopago_service import PLAN_CATALOG


def get_trending_products(db: Session):
    latest = (db.query(TrendSnapshot.product_id, func.max(TrendSnapshot.captured_at).label("at"))
              .group_by(TrendSnapshot.product_id).subquery())
    rows = (
        db.query(
            Product.id,
            Product.title,
            TrendSnapshot.growth_rate,
            PriceHistory.price,
            PriceHistory.sold_quantity,
            TrendSnapshot.captured_at,
        )
        .join(TrendSnapshot, TrendSnapshot.product_id == Product.id)
        .join(latest, (latest.c.product_id == Product.id) & (latest.c.at == TrendSnapshot.captured_at))
        .join(
            PriceHistory,
            (PriceHistory.product_id == Product.id)
            & (PriceHistory.captured_at == TrendSnapshot.captured_at),
        )
        .filter(TrendSnapshot.is_trending.is_(True))
        .order_by(TrendSnapshot.growth_rate.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "product_id": row[0],
            "title": row[1],
            "growth_rate": round(row[2], 4),
            "last_price": row[3],
            "sold_quantity": row[4],
            "captured_at": row[5],
        }
        for row in rows
    ]


def get_price_alerts(db: Session):
    alerts = []
    product_ids = [pid for (pid,) in db.query(PriceHistory.product_id).distinct().all()]

    for product_id in product_ids:
        latest = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.captured_at.desc())
            .limit(2)
            .all()
        )
        if len(latest) < 2:
            continue

        current, previous = latest[0], latest[1]
        if previous.price > 0 and 0 <= current.price < previous.price:
            product = db.query(Product).filter(Product.id == product_id).first()
            diff_pct = ((previous.price - current.price) / previous.price) * 100 if previous.price else 0
            alerts.append(
                {
                    "product_id": product_id,
                    "title": product.title if product else product_id,
                    "previous_price": previous.price,
                    "current_price": current.price,
                    "diff_percentage": round(diff_pct, 2),
                    "captured_at": current.captured_at,
                }
            )

    alerts.sort(key=lambda item: item["diff_percentage"], reverse=True)
    return alerts[:50]


def get_predictions(db: Session):
    latest = (db.query(WeeklyPrediction.product_id,
                       func.max(WeeklyPrediction.captured_at).label("captured_at"))
              .group_by(WeeklyPrediction.product_id).subquery())
    rows = (db.query(WeeklyPrediction, Product)
            .join(Product, Product.id == WeeklyPrediction.product_id)
            .join(latest, (latest.c.product_id == WeeklyPrediction.product_id)
                  & (latest.c.captured_at == WeeklyPrediction.captured_at))
            .order_by(WeeklyPrediction.product_id).all())
    return [{"product_id": product.id, "title": product.title,
             "predicted_sales_next_week": (round(row.predicted_increment, 2)
                                           if row.status == "available" and row.predicted_increment is not None
                                           else None),
             "status": row.status, "horizon_days": 7,
             "model_version": row.model_version, "captured_at": row.captured_at}
            for row, product in rows]


def get_top_sellers(db: Session):
    rows = (
        db.query(
            Product.seller_id,
            func.count(func.distinct(Product.id)),
            func.avg(PriceHistory.sold_quantity),
        )
        .join(PriceHistory, PriceHistory.product_id == Product.id)
        .group_by(Product.seller_id)
        .order_by(func.avg(PriceHistory.sold_quantity).desc())
        .limit(20)
        .all()
    )

    return [
        {
            "seller_id": row[0],
            "total_products": int(row[1]),
            "avg_sales": round(float(row[2] or 0), 2),
        }
        for row in rows
    ]


def get_admin_metrics(db: Session):
    users = db.query(func.count()).select_from(User).scalar() or 0
    active_products = db.query(func.count()).select_from(Product).scalar() or 0
    captures = db.query(func.count()).select_from(PriceHistory).scalar() or 0
    trending = (
        db.query(func.count())
        .select_from(TrendSnapshot)
        .filter(TrendSnapshot.is_trending.is_(True))
        .scalar()
        or 0
    )

    return {
        "captured_at": datetime.utcnow(),
        "total_users": users,
        "active_products": active_products,
        "price_captures": captures,
        "trending_products": trending,
    }


def get_admin_funnel(db: Session):
    since = datetime.utcnow() - timedelta(days=30)
    attempts = db.query(CheckoutAttempt).filter(CheckoutAttempt.created_at >= since).all()

    started = len(attempts)
    approved = sum(1 for a in attempts if a.status == "approved")
    pending = sum(1 for a in attempts if a.status == "pending")
    recovered = sum(1 for a in attempts if a.status == "approved" and a.reminder_sent_at is not None)

    estimated_mrr_ars = 0
    for attempt in attempts:
        if attempt.status != "approved":
            continue
        estimated_mrr_ars += int(PLAN_CATALOG.get(attempt.plan, {}).get("price_ars", 0))

    conversion_rate = round((approved / started) * 100, 2) if started else 0
    recovered_rate = round((recovered / approved) * 100, 2) if approved else 0

    by_plan = {"starter": 0, "pro": 0, "premium": 0}
    for attempt in attempts:
        if attempt.status == "approved" and attempt.plan in by_plan:
            by_plan[attempt.plan] += 1

    return {
        "window_days": 30,
        "checkouts_started": started,
        "payments_approved": approved,
        "payments_pending": pending,
        "recovered_after_reminder": recovered,
        "conversion_rate_pct": conversion_rate,
        "recovered_rate_pct": recovered_rate,
        "estimated_mrr_ars": estimated_mrr_ars,
        "approved_by_plan": by_plan,
        "captured_at": datetime.utcnow(),
    }


def get_pending_checkout_leads(db: Session):
    threshold = datetime.utcnow() - timedelta(hours=2)
    rows = (
        db.query(CheckoutAttempt, User)
        .join(User, User.id == CheckoutAttempt.user_id)
        .filter(
            CheckoutAttempt.status == "pending",
            CheckoutAttempt.created_at <= threshold,
            User.is_active.is_(True),
        )
        .order_by(CheckoutAttempt.created_at.asc())
        .limit(200)
        .all()
    )

    leads = []
    now = datetime.utcnow()
    for attempt, user in rows:
        hours_pending = round((now - attempt.created_at).total_seconds() / 3600, 1)
        leads.append(
            {
                "user_id": user.id,
                "email": user.email,
                "phone": user.phone,
                "plan": attempt.plan,
                "provider": attempt.provider,
                "checkout_url": attempt.checkout_url,
                "created_at": attempt.created_at,
                "hours_pending": hours_pending,
                "reminder_sent": attempt.reminder_sent_at is not None,
            }
        )

    return {"total": len(leads), "leads": leads, "captured_at": now}
