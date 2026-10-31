"""Idempotent isolated classroom fixture. No external calls or real payments."""
import sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from database.session import SessionLocal, engine
from database.migrations import ensure_schema
from models.entities import User, Product, PriceHistory
from auth.security import hash_password
from services.trend_service import run_trend_detection

ensure_schema(engine)
with SessionLocal() as db:
    for email, plan in [('demo@example.com','pro'), ('starter@example.com','starter')]:
        if not db.query(User).filter_by(email=email).first():
            db.add(User(email=email,password_hash=hash_password('DemoTrendML123!'),subscription_plan=plan))
    for index in range(1,4):
        pid=f'DEMO-CLASS-{index}'
        if db.query(Product).filter_by(id=pid).first():
            continue
        db.add(Product(id=pid,title=f'Producto sintético {index}',seller_id='DEMO-SELLER'))
        db.flush()
        for day in range(35):
            db.add(PriceHistory(product_id=pid,price=100*index if day<34 else 80*index,
                sold_quantity=100+day*index*10+max(0,day-27)*index*20,captured_at=datetime(2026,9,27)+timedelta(days=day),
                review_count=0,score=0,data_source='synthetic'))
    db.commit()
    run_trend_detection(db)
print('Demo académica preparada. demo@example.com / DemoTrendML123! (Pro)')
print('Cuenta Starter: starter@example.com / DemoTrendML123!')
