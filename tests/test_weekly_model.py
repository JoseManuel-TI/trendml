import os
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from services.ml_service import PredictionModel, prepare_data
from database.migrations import ensure_schema
from models.entities import Product, PriceHistory, WeeklyPrediction, TrendSnapshot
from services.trend_service import run_trend_detection
from services.analytics_service import get_predictions
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "worker"))
from data_collector import _upsert_product


def history(days=30, source='synthetic', step=1):
    return [SimpleNamespace(product_id='P1', price=100+i, sold_quantity=10+3*i,
                            review_count=0, score=0, data_source=source,
                            captured_at=datetime(2026, 1, 1)+timedelta(days=i*step))
            for i in range(days)]


class ModelTests(unittest.TestCase):
    def test_weekly_increment(self):
        result = PredictionModel().fit_predict(history(), allow_synthetic=True)
        self.assertEqual(result, {'P1': 21.0})

    def test_latest_observation_used(self):
        class Spy:
            def fit(self, X, y): pass
            def predict(self, X):
                self.latest = X.iloc[0].price
                return [21]
        model = PredictionModel()
        model.model = Spy()
        model.fit_predict(history(), allow_synthetic=True)
        self.assertEqual(model.model.latest, 129)

    def test_no_future_target_leakage(self):
        records = history()
        for original in history():
            row = SimpleNamespace(**dict(vars(original), product_id='P2',
                                         captured_at=original.captured_at+timedelta(days=100)))
            row.price += 1000
            records.append(row)
        class Spy:
            def __init__(self): self.maxima = []
            def fit(self, X, y): self.maximum = X.price.max()
            def predict(self, X):
                self.maxima.append(self.maximum)
                return [21]
        model = PredictionModel()
        model.model = Spy()
        model.fit_predict(records, True)
        self.assertLess(model.model.maxima[0], 1000)
        self.assertGreater(model.model.maxima[1], 1000)

    def test_sparse_history_is_not_weekly(self):
        self.assertEqual(PredictionModel().fit_predict(history(step=10), True), {})

    def test_empty_and_short(self):
        self.assertEqual(PredictionModel().fit_predict([], True), {})
        self.assertEqual(PredictionModel().fit_predict(history(8), True), {})

    def test_unknown_and_demo_excluded(self):
        self.assertEqual(PredictionModel().fit_predict(history(source='unknown')), {})
        rows = history(source='verified_import')
        for r in rows: r.product_id = 'DEMO-P1'
        self.assertEqual(PredictionModel().fit_predict(rows), {})

    def test_invalid_values(self):
        rows = history()
        for r in rows: r.price = float('nan')
        self.assertEqual(PredictionModel().fit_predict(rows, True), {})

    def test_latest_invalid_does_not_label_old_prediction_as_current(self):
        rows = history()
        rows[-1].price = float('inf')
        self.assertEqual(PredictionModel().fit_predict(rows, True), {})

    def test_reset_excludes_old_segment(self):
        rows = history()
        rows[-1].sold_quantity = 1
        training, latest = prepare_data(rows, True)
        self.assertTrue(training.empty)
        self.assertEqual(latest.iloc[0].sold_quantity, 1)

    def test_decreasing_and_duplicate_dates(self):
        rows = history()
        for i, r in enumerate(rows): r.sold_quantity = 100-i
        self.assertEqual(PredictionModel().fit_predict(rows, True), {})
        self.assertEqual(PredictionModel().fit_predict(history()+history(), True), {})


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        ensure_schema(self.engine)
        self.db = Session(self.engine)
        self.db.add(Product(id='P1', title='Fixture', seller_id='fixture'))
        self.db.flush()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def add_history(self, source='synthetic'):
        for r in history(source=source): self.db.add(PriceHistory(**vars(r)))
        self.db.commit()

    def test_synthetic_no_fake_prediction(self):
        self.add_history()
        run_trend_detection(self.db)
        response = get_predictions(self.db)
        self.assertEqual(response[0]['status'], 'unverified_data')
        self.assertIsNone(response[0]['predicted_sales_next_week'])

    def test_idempotent_and_latest_only(self):
        self.add_history()
        run_trend_detection(self.db)
        run_trend_detection(self.db)
        self.assertEqual(self.db.query(WeeklyPrediction).count(), 1)
        self.assertEqual(self.db.query(TrendSnapshot).count(), 1)
        self.assertEqual(len(get_predictions(self.db)), 1)

    def test_verified_path(self):
        # Fixture tests contract only; label does not make it real market data.
        self.add_history('verified_import')
        run_trend_detection(self.db)
        self.assertEqual(get_predictions(self.db)[0]['predicted_sales_next_week'], 21)

    def test_failure_keeps_conventional_analytics(self):
        self.add_history('verified_import')
        with patch('services.trend_service.train_prediction_model', side_effect=RuntimeError('fixture failure')):
            run_trend_detection(self.db)
        self.assertEqual(get_predictions(self.db)[0]['status'], 'model_error')
        self.assertIsNone(get_predictions(self.db)[0]['predicted_sales_next_week'])
        self.assertEqual(self.db.query(TrendSnapshot).count(), 1)

    def test_collector_rejects_missing_sales(self):
        self.assertFalse(_upsert_product(self.db, {'id':'P2','price':100,'seller_id':1}))
        self.assertEqual(self.db.query(PriceHistory).count(), 0)

    def test_collector_sqlite_and_source(self):
        self.assertTrue(_upsert_product(self.db, {'id':'P2','title':'Fixture','price':100,'sold_quantity':0,'seller_id':1}))
        self.db.commit()
        self.assertEqual(self.db.query(PriceHistory).one().data_source, 'mercadolibre_api')

    def test_legacy_migration_is_additive(self):
        legacy = create_engine('sqlite:///:memory:')
        with legacy.begin() as conn:
            conn.execute(text('CREATE TABLE price_history (id INTEGER PRIMARY KEY, product_id VARCHAR(50), price FLOAT, sold_quantity INTEGER, review_count INTEGER, score FLOAT, captured_at DATETIME)'))
            conn.execute(text("INSERT INTO price_history VALUES (1,'DEMO-P1',100,10,0,0,'2026-01-01')"))
        ensure_schema(legacy)
        ensure_schema(legacy)
        with legacy.connect() as conn:
            self.assertEqual(conn.execute(text('SELECT data_source FROM price_history')).scalar(), 'synthetic')
        legacy.dispose()


if __name__ == '__main__': unittest.main()
