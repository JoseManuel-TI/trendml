"""Exploratory residual forecasting on a fixed historical cohort; no live DB writes."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from train_uci_v2 import make_features as features_v2, split, estimator as estimator_v2
from train_uci_v2 import VALIDATION_CUTOFFS, COMPARISON_CUTOFF

FEATURES = ['sales_7', 'sales_14', 'sales_28', 'mean_week_56', 'zero_fraction_28',
            'zero_fraction_56', 'relative_variability_28', 'recent_ratio', 'trend_28_56',
            'price', 'price_change_7', 'month', 'weekday']
LABELS = {'forest_v2': 'Random Forest v2', 'residual_forest': 'Corrección RF v3',
          'residual_boosting': 'Corrección boosting v3', 'last_week': 'Semana anterior',
          'mean_4_weeks': 'Promedio de cuatro semanas'}
CANDIDATES = ['residual_forest', 'residual_boosting']


def make_features(observations):
    training, latest = features_v2(observations)  # validates complete daily histories
    available = pd.concat([training, latest], ignore_index=True)
    raw = pd.DataFrame(observations)
    raw['captured_at'] = pd.to_datetime(raw.captured_at)
    extras = []
    for _, group in raw.groupby('product_id'):
        g = group.sort_values('captured_at').copy()
        g['mean_week_56'] = g.daily_units.rolling(56).sum()/8
        g['zero_fraction_28'] = g.daily_units.eq(0).rolling(28).mean()
        g['zero_fraction_56'] = g.daily_units.eq(0).rolling(56).mean()
        extras.append(g[['product_id', 'captured_at', 'mean_week_56',
                         'zero_fraction_28', 'zero_fraction_56']])
    frame = available.merge(pd.concat(extras), on=['product_id', 'captured_at'], validate='one_to_one')
    frame['baseline'] = frame.sales_28/4
    frame['scale'] = frame.baseline+1
    frame['relative_variability_28'] = frame.daily_std_28/(frame.daily_mean_28+1)
    frame['recent_ratio'] = frame.sales_7/frame.scale
    frame['trend_28_56'] = frame.baseline/(frame.mean_week_56+1)
    frame = frame[np.isfinite(frame[FEATURES]).all(axis=1)].copy()
    return frame.dropna(subset=['target']), frame.sort_values('captured_at').groupby('product_id').tail(1)


def estimator(key):
    if key == 'residual_forest':
        return RandomForestRegressor(n_estimators=150, max_depth=8, min_samples_leaf=10,
                                     random_state=42, n_jobs=1)
    if key == 'residual_boosting':
        return HistGradientBoostingRegressor(loss='absolute_error', max_iter=100,
            max_leaf_nodes=15, min_samples_leaf=20, l2_regularization=1,
            early_stopping=False, random_state=42)
    raise ValueError(key)


def fit_residual(frame, key):
    model = estimator(key)
    residual = (frame.target-frame.baseline)/frame.scale
    # Absolute-error boosting weights recover the units scale from normalized residuals.
    model.fit(frame[FEATURES], residual, sample_weight=frame.scale)
    return model


def predict_residual(model, frame):
    # Inference deliberately reads no future target column.
    return np.maximum(0, frame.baseline.to_numpy()+frame.scale.to_numpy()*model.predict(frame[FEATURES]))


def evaluate(frame, cutoff):
    train, test = split(frame, cutoff)
    predictions = {'last_week': test.sales_7.to_numpy(), 'mean_4_weeks': test.baseline.to_numpy()}
    model, features = estimator_v2('forest')
    model.fit(train[features], train.target)
    predictions['forest_v2'] = np.maximum(0, model.predict(test[features]))
    for key in CANDIDATES:
        predictions[key] = predict_residual(fit_residual(train, key), test)
    cases = [{'product_id': row.product_id, 'origin': row.captured_at.date().isoformat(),
              'target_end': row.target_at.date().isoformat(), 'actual': float(row.target),
              'predictions': {key: float(values[i]) for key, values in predictions.items()}}
             for i, (_, row) in enumerate(test.iterrows())]
    return {'cutoff': cutoff, 'training_pairs': len(train),
            'max_training_target': train.target_at.max().date().isoformat(), 'cases': cases,
            'mae': {k: float(np.mean(np.abs(test.target.to_numpy()-v))) for k, v in predictions.items()}}


def run(prepared, output_dir, public_path):
    if pd.Timestamp(prepared['preparation']['selection_cutoff']) > pd.Timestamp(VALIDATION_CUTOFFS[0]):
        raise ValueError('Future product selection')
    frame, latest = make_features(prepared['observations'])
    validation = [evaluate(frame, cutoff) for cutoff in VALIDATION_CUTOFFS]
    averages = {key: float(np.mean([v['mae'][key] for v in validation])) for key in LABELS}
    selected_model = min(CANDIDATES, key=lambda key: averages[key])
    selected_method = min(LABELS, key=lambda key: averages[key])
    comparison = evaluate(frame, COMPARISON_CUTOFF)
    names = {p['id']: p['title'] for p in prepared['products']}
    for case in comparison['cases']:
        case['title'] = names[case['product_id']]
    per_product = []
    for pid, title in names.items():
        cases = [c for c in comparison['cases'] if c['product_id'] == pid]
        per_product.append({'product_id': pid, 'title': title, 'mae': {
            key: float(np.mean([abs(c['actual']-c['predictions'][key]) for c in cases])) for key in LABELS}})
    worst = sorted(comparison['cases'], key=lambda c: abs(c['actual']-c['predictions'][selected_model]), reverse=True)[:5]
    final_model = fit_residual(frame, selected_model)
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump({'model': final_model, 'features': FEATURES, 'method': selected_model,
                 'prediction_rule': 'max(0, baseline + (baseline + 1) * model.predict(features))',
                 'model_version': 'weekly-residual-v3', 'source': prepared['source'],
                 'as_of': latest.captured_at.max().isoformat()}, output_dir/'weekly-model-v3.joblib')
    report = {'version': 'weekly-residual-v3', 'generated_at': datetime.now(timezone.utc).isoformat(),
              'source': prepared['source'], 'preparation': prepared['preparation'], 'features': FEATURES,
              'labels': LABELS, 'validation': validation, 'validation_mae': averages,
              'selected_model': selected_model, 'selected_method': selected_method,
              'comparison': comparison, 'per_product': per_product, 'worst_cases': worst,
              'final_training_pairs': len(frame),
              'limitations': 'All comparison periods have been inspected in prior experiments. Development results only; independent future evaluation required. Fixed August cohort. V2 refitted on the same 56-day-eligible rows. No production promotion.',
              'forecasts': [{'product_id': row.product_id, 'prediction': float(value),
                             'as_of': row.captured_at.date().isoformat(),
                             'status': 'historical_forecast_unvalidated'}
                            for (_, row), value in zip(latest.iterrows(), predict_residual(final_model, latest))]}
    for target in [output_dir/'evaluation-v3.json', public_path]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='work/uci/prepared-v2.json')
    args = parser.parse_args()
    result = run(json.loads(Path(args.input).read_text()), Path('work/uci'),
                 Path('frontend/public/training-results-v3.json'))
    print(json.dumps({k: result[k] for k in ['validation_mae', 'selected_model', 'selected_method']}, indent=2))
    print('November MAE:', result['comparison']['mae'])
