"""Isolated API acceptance tests: never modify the user's database or send email."""
import os
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from main import app
from database.session import get_db
from models.base import Base
from models.entities import User, Product, PriceHistory, TrendSnapshot
from auth.security import verify_password
from services import forecast_service

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        def db_override():
            with self.session() as db:
                yield db
        app.dependency_overrides[get_db] = db_override
        self.client = TestClient(app)
        self.mail = patch('api.auth.send_welcome_email'); self.mail.start()
        self.credentials = {'email':'student@example.com','password':'ValidPassword123!'}
        self.client.post('/api/auth/register', json=self.credentials)
        token = self.client.post('/api/auth/login', json=self.credentials).json()['access_token']
        self.headers = {'Authorization': 'Bearer ' + token}

    def tearDown(self):
        self.mail.stop(); self.client.close(); app.dependency_overrides.clear(); self.engine.dispose()

    def plan(self, value):
        with self.session() as db:
            db.query(User).first().subscription_plan = value; db.commit()

    def test_registration_duplicate_validation_and_hash(self):
        self.assertEqual(self.client.post('/api/auth/register',json=self.credentials).status_code,409)
        self.assertEqual(self.client.post('/api/auth/register',json={'email':'bad','password':'x'}).status_code,422)
        self.assertEqual(self.client.post('/api/auth/register',json={'email':'other@example.com','password':'x'}).status_code,422)
        with self.session() as db:
            user=db.query(User).first()
            self.assertNotEqual(user.password_hash,self.credentials['password'])
            self.assertTrue(verify_password(self.credentials['password'],user.password_hash))
        self.assertNotIn('password_hash', self.client.get('/api/auth/me',headers=self.headers).json())

    def test_login_invalid_session_and_inactive_user(self):
        self.assertEqual(self.client.post('/api/auth/login',json={**self.credentials,'password':'wrong'}).status_code,401)
        self.assertIn(self.client.get('/api/trending').status_code,(401,403))
        self.assertEqual(self.client.get('/api/trending',headers={'Authorization':'Bearer invalid'}).status_code,401)
        with self.session() as db:
            db.query(User).first().is_active=False;db.commit()
        self.assertEqual(self.client.get('/api/auth/me',headers=self.headers).status_code,401)

    def test_plans_empty_data_and_admin_is_not_premium(self):
        self.assertEqual(self.client.get('/api/trending',headers=self.headers).json(),[])
        for path in ['/api/price-alerts','/api/predictions','/api/top-sellers']:
            self.assertEqual(self.client.get(path,headers=self.headers).status_code,403)
        self.plan('pro')
        for path in ['/api/price-alerts','/api/predictions']:
            self.assertEqual(self.client.get(path,headers=self.headers).json(),[])
        self.plan('premium')
        for path in ['/api/admin/metrics','/api/admin/funnel','/api/admin/pending-leads']:
            self.assertEqual(self.client.get(path,headers=self.headers).status_code,403)

    def test_price_drop_and_latest_trend_only(self):
        self.plan('pro'); now=datetime(2026,1,2)
        with self.session() as db:
            db.add(Product(id='P',title='Test',seller_id='S'));db.flush()
            for day,price in [(now-timedelta(days=1),100),(now,80)]:
                db.add(PriceHistory(product_id='P',price=price,sold_quantity=10,captured_at=day))
                db.add(TrendSnapshot(product_id='P',growth_rate=.5,is_trending=True,captured_at=day))
            db.commit()
        alert=self.client.get('/api/price-alerts',headers=self.headers).json()[0]
        self.assertEqual(alert['diff_percentage'],20)
        self.assertEqual(len(self.client.get('/api/trending',headers=self.headers).json()),1)
        with self.session() as db:
            db.query(PriceHistory).order_by(PriceHistory.captured_at).first().price=0;db.commit()
        self.assertEqual(self.client.get('/api/price-alerts',headers=self.headers).json(),[])

    def test_live_inference_permissions_and_missing_model(self):
        self.assertEqual(self.client.post('/api/lab/forecast',headers=self.headers,json={'product_id':'P'}).status_code,403)
        self.plan('pro')
        self.assertEqual(self.client.post('/api/lab/forecast',headers=self.headers,json={'product_id':''}).status_code,422)
        with patch.object(forecast_service,'forecast',side_effect=FileNotFoundError):
            self.assertEqual(self.client.post('/api/lab/forecast',headers=self.headers,json={'product_id':'P'}).status_code,503)

    @unittest.skipUnless(forecast_service.MODEL_PATH.exists() and forecast_service.DATA_PATH.exists(),'Run UCI preparation and v3 training first')
    def test_real_saved_model_inference(self):
        self.plan('pro')
        products=self.client.get('/api/lab/products',headers=self.headers)
        self.assertEqual(products.status_code,200)
        pid=products.json()['products'][0]['product_id']
        response=self.client.post('/api/lab/forecast',headers=self.headers,json={'product_id':pid})
        self.assertEqual(response.status_code,200)
        data=response.json()
        self.assertGreaterEqual(data['prediction'],0)
        self.assertEqual(data['status'],'historical_forecast_unvalidated')
        self.assertEqual((datetime.fromisoformat(data['target_end'])-datetime.fromisoformat(data['as_of'])).days,7)
        self.assertEqual(self.client.post('/api/lab/forecast',headers=self.headers,json={'product_id':'missing'}).status_code,404)

    def test_adversarial_daily_observations(self):
        from train_uci_v3 import make_features
        for value in [-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):
                make_features([{'product_id':'P','captured_at':'2011-01-01','daily_units':value,'sold_quantity':0,'price':10}])

    def test_academic_mode_disables_checkout(self):
        response=self.client.post('/api/subscriptions/checkout',headers=self.headers,json={'plan':'premium'})
        self.assertEqual(response.status_code,403)
        self.assertEqual(self.client.get('/api/auth/me',headers=self.headers).json()['subscription_plan'],'starter')

    def test_empty_dataset_rejected(self):
        from train_uci_v3 import make_features
        with self.assertRaises(ValueError): make_features([])
