"""On-demand inference from the trusted, locally trained UCI artifact.

No user-supplied pickle paths and no retraining during HTTP requests.
"""
import json
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from train_uci_v3 import FEATURES, make_features, predict_residual

MODEL_PATH = ROOT / 'work/uci/weekly-model-v3.joblib'
DATA_PATH = ROOT / 'work/uci/prepared-v2.json'


@lru_cache(maxsize=1)
def _load(model_stamp, data_stamp):
    artifact = joblib.load(MODEL_PATH)  # trusted local build only
    prepared = json.loads(DATA_PATH.read_text())
    if artifact['model_version'] != 'weekly-residual-v3' or artifact['features'] != FEATURES:
        raise ValueError('Incompatible model artifact')
    artifact_hash = (artifact.get('source') or {}).get('archive_sha256')
    prepared_hash = (prepared.get('source') or {}).get('archive_sha256')
    if artifact_hash and prepared_hash and artifact_hash != prepared_hash:
        raise ValueError('Model and prepared data come from different archives')
    trained_through = artifact.get('trained_through')
    if trained_through and pd.Timestamp(trained_through) > pd.Timestamp(artifact['as_of']):
        raise ValueError('Model was trained with targets after its inference cutoff')
    _, latest = make_features(prepared['observations'])
    if latest.empty or not latest.captured_at.eq(pd.Timestamp(artifact['as_of'])).all():
        raise ValueError('Model and observation dates do not match')
    names = {p['id']: p['title'] for p in prepared['products']}
    if set(latest.product_id) != set(names):
        raise ValueError('Model catalog and prepared products do not match')
    return artifact, latest, names


def resources():
    return _load(MODEL_PATH.stat().st_mtime_ns, DATA_PATH.stat().st_mtime_ns)


def _provenance(artifact):
    return {
        'model_version': artifact['model_version'],
        'method': artifact.get('method'),
        'trained_through': artifact.get('trained_through'),
        'training_pairs': artifact.get('training_pairs'),
        'validation_cutoffs': artifact.get('validation_cutoffs'),
        'comparison_cutoff': artifact.get('comparison_cutoff'),
        'validation_mae': artifact.get('validation_mae'),
        'reference_mae': artifact.get('reference_mae'),
        'model_generated_at': artifact.get('generated_at'),
        'limitations': artifact.get('limitations'),
    }


def catalog():
    artifact, latest, names = resources()
    return {'source': artifact['source'], **_provenance(artifact),
            'products': [{'product_id': r.product_id, 'title': names[r.product_id],
                          'as_of': r.captured_at.date().isoformat()}
                         for _, r in latest.iterrows()]}


def forecast(product_id):
    artifact, latest, names = resources()
    row = latest[latest.product_id == product_id]
    if row.empty:
        raise KeyError(product_id)
    value = float(predict_residual(artifact['model'], row)[0])
    if not np.isfinite(value):
        raise ValueError('Nonfinite model prediction')
    origin = row.iloc[0].captured_at
    result = {'product_id': product_id, 'title': names[product_id],
              'prediction': value, 'baseline': float(row.iloc[0].baseline),
              'as_of': origin.date().isoformat(),
              'target_start': (origin + pd.Timedelta(days=1)).date().isoformat(),
              'target_end': (origin + pd.Timedelta(days=7)).date().isoformat(),
              'horizon_days': 7, 'source': artifact['source'],
              'status': 'historical_forecast_unvalidated',
              'computed_at': datetime.now(timezone.utc).isoformat()}
    result.update(_provenance(artifact))
    return result
