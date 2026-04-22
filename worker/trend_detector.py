import os
from collections import defaultdict

import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://trendml:trendml@postgres:5432/trendml")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_table(db):
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS trend_snapshots (
                id SERIAL PRIMARY KEY,
                product_id VARCHAR(50) NOT NULL,
                growth_rate FLOAT NOT NULL,
                predicted_sales_next_week FLOAT NOT NULL DEFAULT 0,
                is_trending BOOLEAN NOT NULL DEFAULT FALSE,
                captured_at TIMESTAMP NOT NULL,
                CONSTRAINT uq_trend_product_time UNIQUE (product_id, captured_at),
                CONSTRAINT fk_trend_product FOREIGN KEY(product_id) REFERENCES products(id)
            );
            """
        )
    )
    db.commit()


def _predict(df: pd.DataFrame) -> dict[str, float]:
    if len(df) < 10:
        return {}

    frame = df.copy()
    frame["target"] = frame.groupby("product_id")["sold_quantity"].shift(-1)
    frame = frame.dropna()
    if frame.empty:
        return {}

    X = frame[["price", "sold_quantity", "review_count", "score"]]
    y = frame["target"]

    model = RandomForestRegressor(n_estimators=40, random_state=42)
    model.fit(X, y)

    latest = frame.groupby("product_id").tail(1)
    preds = model.predict(latest[["price", "sold_quantity", "review_count", "score"]])
    return {pid: float(p) for pid, p in zip(latest["product_id"].tolist(), preds)}


def process_trends():
    db = SessionLocal()
    try:
        _ensure_table(db)
        rows = db.execute(
            text(
                """
                SELECT product_id, price, sold_quantity, review_count, score, captured_at
                FROM price_history
                ORDER BY captured_at ASC
                """
            )
        ).mappings().all()

        if not rows:
            return 0

        df = pd.DataFrame(rows)
        predictions = _predict(df)

        by_product = defaultdict(list)
        for row in rows:
            by_product[row["product_id"]].append(row)

        inserted = 0
        for product_id, items in by_product.items():
            if len(items) < 2:
                continue

            latest = items[-1]
            base = items[-8] if len(items) > 8 else items[0]
            previous_sales = int(base["sold_quantity"] or 0)
            current_sales = int(latest["sold_quantity"] or 0)

            growth_rate = ((current_sales - previous_sales) / previous_sales) if previous_sales > 0 else 0
            db.execute(
                text(
                    """
                    INSERT INTO trend_snapshots (product_id, growth_rate, predicted_sales_next_week, is_trending, captured_at)
                    VALUES (:product_id, :growth_rate, :predicted, :is_trending, :captured_at)
                    ON CONFLICT (product_id, captured_at) DO NOTHING
                    """
                ),
                {
                    "product_id": product_id,
                    "growth_rate": float(growth_rate),
                    "predicted": float(predictions.get(product_id, current_sales)),
                    "is_trending": growth_rate > 0.30,
                    "captured_at": latest["captured_at"],
                },
            )
            inserted += 1

        db.commit()
        return inserted
    finally:
        db.close()


if __name__ == "__main__":
    processed = process_trends()
    print(f"[trend-detector] processed snapshots: {processed}")
