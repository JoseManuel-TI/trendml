import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://trendml:trendml@postgres:5432/trendml")
ML_SITE = os.getenv("ML_SITE", "MLA")
ML_QUERIES = os.getenv("ML_QUERIES", "notebook,auriculares,mouse gamer").split(",")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_tables(db):
    db.execute(
        text(
            """
        CREATE TABLE IF NOT EXISTS products (
            id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            seller_id VARCHAR(50) NOT NULL,
            category_id VARCHAR(50),
            permalink VARCHAR(500)
        );
        """
        )
    )
    db.execute(
        text(
            """
        CREATE TABLE IF NOT EXISTS price_history (
            id SERIAL PRIMARY KEY,
            product_id VARCHAR(50) NOT NULL,
            price FLOAT NOT NULL,
            sold_quantity INT NOT NULL,
            review_count INT NOT NULL DEFAULT 0,
            score FLOAT NOT NULL DEFAULT 0,
            captured_at TIMESTAMP NOT NULL,
            CONSTRAINT fk_product FOREIGN KEY(product_id) REFERENCES products(id)
        );
        """
        )
    )
    db.commit()


def _upsert_product(db, item):
    product_id = item.get("id")
    if not product_id:
        return

    db.execute(
        text(
            """
        INSERT INTO products (id, title, seller_id, category_id, permalink)
        VALUES (:id, :title, :seller_id, :category_id, :permalink)
        ON CONFLICT (id) DO UPDATE
        SET title = EXCLUDED.title,
            seller_id = EXCLUDED.seller_id,
            category_id = EXCLUDED.category_id,
            permalink = EXCLUDED.permalink;
        """
        ),
        {
            "id": product_id,
            "title": item.get("title", ""),
            "seller_id": str(item.get("seller", {}).get("id", "unknown")),
            "category_id": item.get("category_id"),
            "permalink": item.get("permalink"),
        },
    )

    reviews = item.get("reviews", {}) or {}
    db.execute(
        text(
            """
        INSERT INTO price_history (product_id, price, sold_quantity, review_count, score, captured_at)
        VALUES (:product_id, :price, :sold_quantity, :review_count, :score, :captured_at);
        """
        ),
        {
            "product_id": product_id,
            "price": float(item.get("price", 0) or 0),
            "sold_quantity": int(item.get("sold_quantity", 0) or 0),
            "review_count": int(reviews.get("total", 0) or 0),
            "score": float(reviews.get("rating_average", 0) or 0),
            "captured_at": datetime.utcnow(),
        },
    )


def collect_market_data():
    db = SessionLocal()
    inserted = 0
    try:
        _ensure_tables(db)
        for query in ML_QUERIES:
            query = query.strip()
            if not query:
                continue
            url = f"https://api.mercadolibre.com/sites/{ML_SITE}/search"
            response = requests.get(url, params={"q": query, "limit": 50}, timeout=20)
            response.raise_for_status()
            payload = response.json()

            for item in payload.get("results", []):
                _upsert_product(db, item)
                inserted += 1

        db.commit()
    finally:
        db.close()

    return inserted


if __name__ == "__main__":
    total = collect_market_data()
    print(f"[collector] records processed: {total}")
