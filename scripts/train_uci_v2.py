"""Historical v2 experiment. Shared dated splits, past-only features, no live DB writes."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor

FEATURES = ['sales_7', 'sales_14', 'sales_28', 'daily_mean_28', 'daily_std_28',
            'previous_week', 'weekly_change', 'price', 'price_change_7', 'month', 'weekday']
OLD_FEATURES = ['price', 'sold_quantity', 'review_count', 'score']
LABELS = {'current': 'Modelo actual (v1)', 'forest': 'Random Forest v2',
          'boosting': 'Boosting v2', 'last_week': 'Semana anterior',
          'mean_4_weeks': 'Promedio de cuatro semanas'}
VALIDATION_CUTOFFS = ['2011-08-01', '2011-09-01', '2011-10-01']
COMPARISON_CUTOFF = '2011-11-01'


def make_features(observations):
    raw = pd.DataFrame(observations)
    required = {'product_id', 'captured_at', 'daily_units', 'sold_quantity', 'price'}
    if raw.empty or not required.issubset(raw.columns):
        raise ValueError('Missing daily observations or required fields')
    numeric = raw[['daily_units', 'sold_quantity', 'price']]
    if not np.isfinite(numeric.to_numpy(dtype=float)).all() or (numeric < 0).any().any():
        raise ValueError('Sales and prices must be finite and nonnegative')
    raw['captured_at'] = pd.to_datetime(raw.captured_at)
    if raw.duplicated(['product_id', 'captured_at']).any():
        raise ValueError('Duplicate daily observations')
    frames = []
    for _, group in raw.groupby('product_id'):
        g = group.sort_values('captured_at').copy()
        if not g.captured_at.diff().dropna().eq(pd.Timedelta(days=1)).all():
            raise ValueError('Daily history must be complete; do not invent missing observations')
        if (g.sold_quantity.diff().dropna() < 0).any():
            raise ValueError('Cumulative sales reset')
        if not np.allclose(g.sold_quantity.diff().iloc[1:], g.daily_units.iloc[1:]):
            raise ValueError('Daily units disagree with cumulative sales')
        units = g.daily_units
        for days in [7, 14, 28]:
            g[f'sales_{days}'] = units.rolling(days, min_periods=days).sum()
        g['daily_mean_28'] = units.rolling(28).mean()
        g['daily_std_28'] = units.rolling(28).std()
        g['previous_week'] = g.sales_7.shift(7)
        g['weekly_change'] = g.sales_7 - g.previous_week
        g['price_change_7'] = g.price / g.price.shift(7) - 1
        g['month'] = g.captured_at.dt.month
        g['weekday'] = g.captured_at.dt.dayofweek
        g['target'] = g.sold_quantity.shift(-7) - g.sold_quantity
        g['target_at'] = g.captured_at + pd.Timedelta(days=7)
        frames.append(g)
    frame = pd.concat(frames, ignore_index=True)
    valid = np.isfinite(frame[FEATURES]).all(axis=1)
    frame = frame[valid].copy()
    latest = frame.sort_values('captured_at').groupby('product_id').tail(1)
    return frame.dropna(subset=['target']), latest


def split(frame, cutoff):
    cutoff = pd.Timestamp(cutoff)
    origins = [cutoff + pd.Timedelta(days=7*i) for i in range(4)]
    train = frame[frame.target_at <= cutoff].copy()
    test = frame[frame.captured_at.isin(origins)].copy()
    if train.empty or test.empty or train.target_at.max() > test.captured_at.min():
        raise ValueError('Invalid temporal split')
    expected = len(frame.product_id.unique()) * 4
    if len(test) != expected:
        raise ValueError('Incomplete product/week comparison')
    return train, test


def estimator(key):
    if key == 'current':
        return RandomForestRegressor(n_estimators=50, random_state=42), OLD_FEATURES
    if key == 'forest':
        return RandomForestRegressor(n_estimators=150, max_depth=10,
                                     min_samples_leaf=5, random_state=42, n_jobs=1), FEATURES
    if key == 'boosting':
        return HistGradientBoostingRegressor(max_iter=100, max_leaf_nodes=15,
            l2_regularization=1, random_state=42, early_stopping=False), FEATURES
    raise ValueError(key)


def evaluate(frame, cutoff):
    train, test = split(frame, cutoff)
    predictions = {'last_week': test.sales_7.to_numpy(),
                   'mean_4_weeks': test.sales_28.to_numpy()/4}
    for key in ['current', 'forest', 'boosting']:
        model, features = estimator(key)
        model.fit(train[features], train.target)
        predictions[key] = np.maximum(0, model.predict(test[features]))
    cases = []
    for i, (_, row) in enumerate(test.iterrows()):
        cases.append({'product_id': row.product_id, 'origin': row.captured_at.date().isoformat(),
                      'target_end': row.target_at.date().isoformat(), 'actual': float(row.target),
                      'predictions': {k: float(v[i]) for k, v in predictions.items()}})
    metrics = {k: float(np.mean(np.abs(test.target.to_numpy()-v))) for k, v in predictions.items()}
    return {'cutoff': cutoff, 'training_pairs': len(train), 'cases': cases, 'mae': metrics,
            'max_training_target': train.target_at.max().date().isoformat()}


def run(prepared, output_dir, public_path):
    if pd.Timestamp(prepared['preparation']['selection_cutoff']) > pd.Timestamp(VALIDATION_CUTOFFS[0]):
        raise ValueError('Product selection must precede every validation origin')
    frame, latest = make_features(prepared['observations'])
    validation = [evaluate(frame, c) for c in VALIDATION_CUTOFFS]
    averages = {k: float(np.mean([f['mae'][k] for f in validation])) for k in LABELS}
    # Freeze model selection before examining November. No tuning on November.
    selected_model = min(['forest', 'boosting'], key=lambda k: averages[k])
    selected_method = min(LABELS, key=lambda k: averages[k])
    comparison = evaluate(frame, COMPARISON_CUTOFF)
    per_product = []
    names = {p['id']: p['title'] for p in prepared['products']}
    for pid, title in names.items():
        cases = [c for c in comparison['cases'] if c['product_id'] == pid]
        per_product.append({'product_id': pid, 'title': title, 'mae': {
            k: float(np.mean([abs(c['actual']-c['predictions'][k]) for c in cases])) for k in LABELS}})
    for case in comparison['cases']:
        case['title'] = names[case['product_id']]
    model, features = estimator(selected_model)
    model.fit(frame[features], frame.target)
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump({'model': model, 'features': features, 'model_version': 'weekly-lags-v2',
                 'method': selected_model, 'as_of': latest.captured_at.max().isoformat(),
                 'source': prepared['source']}, output_dir/'weekly-model-v2.joblib')
    report = {'version': 'weekly-lags-v2', 'generated_at': datetime.now(timezone.utc).isoformat(),
              'source': prepared['source'], 'preparation': prepared['preparation'],
              'features': FEATURES, 'labels': LABELS, 'validation': validation,
              'validation_mae': averages, 'selected_model': selected_model,
              'selected_method': selected_method, 'comparison': comparison,
              'per_product': per_product, 'final_training_pairs': len(frame),
              'limitations': 'November was previously inspected: exploratory comparison, not an independent final test. Cohort selected on August 1; v1 refitted on identical eligible rows. No production promotion.',
              'forecasts': [{'product_id': row.product_id, 'prediction': float(max(0, value)),
                             'as_of': row.captured_at.date().isoformat(),
                             'status': 'historical_forecast_unvalidated'}
                            for (_, row), value in zip(latest.iterrows(), model.predict(latest[features]))]}
    for path in [output_dir/'evaluation-v2.json', public_path]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='work/uci/prepared-v2.json')
    args = parser.parse_args()
    report = run(json.loads(Path(args.input).read_text()), Path('work/uci'),
                 Path('frontend/public/training-results-v2.json'))
    print(json.dumps({k: report[k] for k in ['validation_mae', 'selected_model', 'selected_method']}, indent=2))
    print('November MAE:', report['comparison']['mae'])
