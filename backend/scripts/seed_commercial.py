from __future__ import annotations

from datetime import datetime, timedelta
from random import randint, choice, random

from auth.security import hash_password
from database.session import SessionLocal, engine
from models.base import Base
from models.entities import CheckoutAttempt, PriceHistory, Product, TrendSnapshot, User


def seed_users_and_attempts():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        users = []
        for i in range(1, 21):
            email = f"seller{i}@example.com"
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    phone=f"54911{randint(20000000, 99999999)}",
                    password_hash=hash_password("Password123!"),
                    subscription_plan=choice(["starter", "pro", "premium"]),
                    is_active=True,
                )
                db.add(user)
                db.flush()
            elif not user.phone:
                user.phone = f"54911{randint(20000000, 99999999)}"
                db.add(user)
            users.append(user)

        now = datetime.utcnow()
        for _ in range(80):
            user = choice(users)
            plan = choice(["starter", "pro", "premium", "pro", "pro"])
            created_at = now - timedelta(hours=randint(1, 120), minutes=randint(0, 59))
            status = "approved" if random() > 0.45 else "pending"
            reminder_sent_at = None
            if status == "approved" and random() > 0.7:
                reminder_sent_at = created_at + timedelta(hours=26)

            attempt = CheckoutAttempt(
                user_id=user.id,
                plan=plan,
                provider="mercadopago",
                preference_id=f"pref_{randint(100000, 999999)}",
                checkout_url="https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=demo",
                status=status,
                created_at=created_at,
                reminder_sent_at=reminder_sent_at,
            )
            db.add(attempt)

        db.commit()
    finally:
        db.close()


def seed_market_data():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        products = []
        for i in range(1, 31):
            pid = f"MLA{i:06d}"
            product = db.query(Product).filter(Product.id == pid).first()
            if not product:
                product = Product(
                    id=pid,
                    title=f"Producto demo {i}",
                    seller_id=str(randint(1000, 9999)),
                    category_id="MLA1055",
                    permalink="https://articulo.mercadolibre.com.ar/demo",
                )
                db.add(product)
                db.flush()
            products.append(product)

        for p in products:
            base_sales = randint(50, 1000)
            for d in range(10, -1, -1):
                captured = now - timedelta(days=d)
                sold = base_sales + randint(-50, 140)
                price = randint(7000, 120000)
                db.add(
                    PriceHistory(
                        product_id=p.id,
                        price=float(price),
                        sold_quantity=max(1, sold),
                        review_count=randint(10, 500),
                        score=round(3 + random() * 2, 2),
                        captured_at=captured,
                    )
                )

            growth = round(random() * 0.8, 4)
            db.add(
                TrendSnapshot(
                    product_id=p.id,
                    growth_rate=growth,
                    predicted_sales_next_week=float(base_sales + randint(100, 350)),
                    is_trending=growth > 0.30,
                    captured_at=now,
                )
            )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users_and_attempts()
    seed_market_data()
    print("[seed] commercial demo data inserted")
