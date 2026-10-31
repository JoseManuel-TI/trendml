"""Seven-day increments of an exact, cumulative sales counter.

Only verified observations are eligible. Synthetic fixtures may explicitly opt in
in tests, but production never trains on DEMO/unknown observations.
"""
from datetime import timedelta
import math
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy.orm import Session
from models.entities import PriceHistory

HORIZON_DAYS = 7
MODEL_VERSION = "weekly-increment-v1"
VERIFIED_SOURCES = {"mercadolibre_api", "verified_import"}
FEATURES = ["price", "sold_quantity", "review_count", "score"]
MIN_TRAINING_PAIRS = 10


def prepare_data(records, allow_synthetic=False):
    rows = []
    for r in records:
        source = getattr(r, "data_source", "unknown")
        if source not in VERIFIED_SOURCES and not (allow_synthetic and source == "synthetic"):
            continue
        if str(r.product_id).startswith("DEMO-") and not allow_synthetic:
            continue
        try:
            values = [float(getattr(r, f)) for f in FEATURES]
            if not all(math.isfinite(v) and v >= 0 for v in values):
                continue
            if values[1] != int(values[1]) or values[2] != int(values[2]) or values[3] > 5:
                continue
            timestamp = pd.Timestamp(r.captured_at)
            if pd.isna(timestamp):
                continue
        except (TypeError, ValueError, OverflowError):
            continue
        rows.append(dict(zip(FEATURES, values), product_id=r.product_id,
                         captured_at=timestamp))
    if not rows:
        return pd.DataFrame(), pd.DataFrame()
    frame = pd.DataFrame(rows).sort_values("captured_at")
    # Conflicting observations at one instant are not trustworthy.
    frame = frame.drop_duplicates(["product_id", "captured_at"], keep=False)
    training = []
    latest = []
    for _, group in frame.groupby("product_id"):
        group = group.sort_values("captured_at")
        # A decreasing cumulative counter implies a reset. Only the segment
        # after the last reset is comparable with the present observation.
        resets = group["sold_quantity"].diff() < 0
        if resets.any():
            group = group.iloc[[i for i, reset in enumerate(resets) if reset][-1]:]
        if group.empty:
            continue
        latest.append(group.iloc[-1].to_dict())
        for _, row in group.iterrows():
            target_time = row.captured_at + timedelta(days=HORIZON_DAYS)
            # A capture within one hour of the seven-day instant is accepted;
            # sparse records cannot silently turn into a weekly target.
            future = group[(group.captured_at >= target_time)
                           & (group.captured_at <= target_time + timedelta(hours=1))]
            if future.empty:
                continue
            end = future.iloc[0]
            training.append(dict(row, target=end.sold_quantity - row.sold_quantity,
                                 target_at=end.captured_at))
    return pd.DataFrame(training), pd.DataFrame(latest)


class PredictionModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)

    def fit_predict(self, records, allow_synthetic=False):
        training, latest = prepare_data(records, allow_synthetic)
        if training.empty or latest.empty:
            return {}
        results = {}
        newest = {}
        for record in records:
            try:
                instant = pd.Timestamp(record.captured_at)
                if not pd.isna(instant):
                    newest[record.product_id] = max(instant, newest.get(record.product_id, instant))
            except (TypeError, ValueError):
                continue
        # Each prediction uses only targets already known at its observation.
        for _, row in latest.iterrows():
            if newest.get(row.product_id) != row.captured_at:
                continue
            known = training[training.target_at <= row.captured_at]
            if len(known) < MIN_TRAINING_PAIRS or row.product_id not in set(known.product_id):
                continue
            self.model.fit(known[FEATURES], known.target)
            value = float(self.model.predict(pd.DataFrame([row])[FEATURES])[0])
            if math.isfinite(value) and value >= 0:
                results[row.product_id] = value
        return results


def train_prediction_model(db: Session):
    records = db.query(PriceHistory).order_by(PriceHistory.captured_at.asc()).all()
    return PredictionModel().fit_predict(records)
