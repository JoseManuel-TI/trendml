"""Collect exact counters from an authorized seller, never fill missing sales with 0."""
import math
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from database.session import engine, SessionLocal
from database.migrations import ensure_schema
from models.entities import Product, PriceHistory


def _upsert_product(db, item):
    quantity = item.get("sold_quantity")
    price = item.get("price")
    if not item.get("id") or isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
        return False
    if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
        return False
    product = db.get(Product, item["id"])
    if product is None:
        product = Product(id=item["id"])
        db.add(product)
    product.title = item.get("title") or item["id"]
    product.seller_id = str(item["seller_id"])
    product.category_id = item.get("category_id")
    product.permalink = item.get("permalink")
    db.flush()
    # Reviews are omitted when unavailable, rather than fabricated features.
    # The current model uses these zeros as an explicit neutral feature.
    db.add(PriceHistory(product_id=product.id, price=price, sold_quantity=quantity,
                        review_count=0, score=0, captured_at=datetime.utcnow(),
                        data_source="mercadolibre_api"))
    return True


def collect_market_data():
    token = os.getenv("ML_ACCESS_TOKEN")
    seller = os.getenv("ML_SELLER_ID")
    if not token or not seller:
        raise RuntimeError("Configure ML_ACCESS_TOKEN y ML_SELLER_ID de una cuenta vendedora autorizada; no se generan datos demo.")
    headers = {"Authorization": f"Bearer {token}"}
    # Verify token ownership without logging the token or user details.
    response = requests.get("https://api.mercadolibre.com/users/me", headers=headers, timeout=20)
    response.raise_for_status()
    if str(response.json().get("id")) != seller:
        raise ValueError("El token no corresponde a ML_SELLER_ID")
    ensure_schema(engine)
    count, offset = 0, 0
    with SessionLocal() as db:
        seen = set()
        while True:
            response = requests.get(f"https://api.mercadolibre.com/users/{seller}/items/search",
                                    headers=headers, params={"limit": 50, "offset": offset}, timeout=20)
            response.raise_for_status()
            payload = response.json()
            ids = payload.get("results", [])
            if not ids:
                break
            for item_id in ids:
                if item_id in seen:
                    continue
                seen.add(item_id)
                result = requests.get(f"https://api.mercadolibre.com/items/{item_id}", headers=headers, timeout=20)
                result.raise_for_status()
                item = result.json()
                if str(item.get("seller_id")) != seller:
                    raise ValueError("Producto fuera de la cuenta autorizada")
                count += int(_upsert_product(db, item))
            offset += len(ids)
            if offset >= min(int(payload.get("paging", {}).get("total", offset)), 1000):
                break
        db.commit()
    return count


if __name__ == "__main__":
    print(f"[collector] valid observations: {collect_market_data()}")
