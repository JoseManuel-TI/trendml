import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy.orm import Session

from models.entities import PriceHistory


class PredictionModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)

    def fit_predict(self, records: list[PriceHistory]) -> dict[str, float]:
        if len(records) < 10:
            return {}

        data = pd.DataFrame(
            [
                {
                    "product_id": r.product_id,
                    "price": r.price,
                    "sold_quantity": r.sold_quantity,
                    "review_count": r.review_count,
                    "score": r.score,
                }
                for r in records
            ]
        )

        data["target"] = data.groupby("product_id")["sold_quantity"].shift(-1)
        data = data.dropna()
        if data.empty:
            return {}

        X = data[["price", "sold_quantity", "review_count", "score"]]
        y = data["target"]
        self.model.fit(X, y)

        latest = data.groupby("product_id").tail(1)
        latest_X = latest[["price", "sold_quantity", "review_count", "score"]]
        preds = self.model.predict(latest_X)

        return {pid: float(pred) for pid, pred in zip(latest["product_id"].tolist(), preds)}


def train_prediction_model(db: Session) -> dict[str, float]:
    records = db.query(PriceHistory).order_by(PriceHistory.captured_at.asc()).all()
    model = PredictionModel()
    return model.fit_predict(records)
