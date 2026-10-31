"""Use the same model and persistence as the backend."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from database.session import engine, SessionLocal
from database.migrations import ensure_schema
from services.trend_service import run_trend_detection


def process_trends():
    ensure_schema(engine)
    with SessionLocal() as db:
        return run_trend_detection(db)


if __name__ == "__main__":
    print(f"[trend-detector] processed snapshots: {process_trends()}")
