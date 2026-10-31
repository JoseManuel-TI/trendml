"""Reproducible historical evaluation and final model training. No live DB writes."""
import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone
import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from services.ml_service import prepare_data, PredictionModel, FEATURES, MODEL_VERSION


def temporal_split(training, cutoff, origins):
    cutoff=pd.Timestamp(cutoff)
    train=training[training.target_at <= cutoff].copy()
    test=training[training.captured_at.isin(pd.to_datetime(origins))].copy()
    if train.empty or test.empty:
        raise ValueError('Insufficient temporal coverage')
    if train.target_at.max() > test.captured_at.min():
        raise ValueError('Training targets overlap evaluation period')
    return train,test


def run(prepared):
    records=[SimpleNamespace(**dict(r,captured_at=pd.Timestamp(r['captured_at']).to_pydatetime()))
             for r in prepared['observations']]
    training,latest=prepare_data(records)
    cutoff='2011-11-01'
    origins=['2011-11-01','2011-11-08','2011-11-15','2011-11-22']
    train,test=temporal_split(training,cutoff,origins)
    model=PredictionModel().model
    model.fit(train[FEATURES],train.target)
    predicted=model.predict(test[FEATURES])
    lookup={(r.product_id,pd.Timestamp(r.captured_at)):r.sold_quantity for r in records}
    names={p['id']:p['title'] for p in prepared['products']}
    cases=[]
    for (_,row),value in zip(test.iterrows(),predicted):
        baseline=row.sold_quantity-lookup[(row.product_id,row.captured_at-pd.Timedelta(days=7))]
        cases.append({'product_id':row.product_id,'title':names[row.product_id],
                      'origin':row.captured_at.date().isoformat(),
                      'target_end':row.target_at.date().isoformat(),
                      'actual':float(row.target),'prediction':float(value),
                      'baseline':float(baseline),'absolute_error':abs(float(value)-row.target)})
    mae=mean_absolute_error([c['actual'] for c in cases],[c['prediction'] for c in cases])
    baseline_mae=mean_absolute_error([c['actual'] for c in cases],[c['baseline'] for c in cases])
    # After freezing evaluation, retrain for the end-of-history forecast.
    final_model=PredictionModel().model
    final_model.fit(training[FEATURES],training.target)
    final_values=final_model.predict(latest[FEATURES])
    forecasts=[{'product_id':row.product_id,'title':names[row.product_id],
                'as_of':row.captured_at.date().isoformat(),
                'target_end':(row.captured_at+pd.Timedelta(days=7)).date().isoformat(),
                'prediction':float(value),'status':'historical_forecast_unvalidated'}
               for (_,row),value in zip(latest.iterrows(),final_values)]
    report={'source':prepared['source'],'preparation':prepared['preparation'],
            'generated_at':datetime.now(timezone.utc).isoformat(),
            'model_version':MODEL_VERSION,'features':FEATURES,
            'evaluation':{'cutoff':cutoff,'origins':origins,'training_pairs':len(train),
                          'test_cases':len(cases),'products':len(names),
                          'mae':float(mae),'baseline_mae':float(baseline_mae),
                          'beats_baseline':bool(mae<baseline_mae),
                          'max_training_target':train.target_at.max().date().isoformat(),
                          'min_test_origin':test.captured_at.min().date().isoformat(),
                          'method':'Fixed training cutoff; four non-overlapping weekly evaluation windows; no tuning on test'},
            'final_training_pairs':len(training),'cases':cases,'forecasts':forecasts}
    return report,final_model


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',default='work/uci/prepared.json')
    args=parser.parse_args()
    prepared=json.loads(Path(args.input).read_text())
    report,model=run(prepared)
    folder=Path('work/uci');folder.mkdir(parents=True,exist_ok=True)
    joblib.dump({'model':model,'features':FEATURES,'source':report['source'],
                 'as_of':'2011-12-08','model_version':MODEL_VERSION},folder/'weekly-model.joblib')
    for target in [folder/'evaluation.json',Path('frontend/public/training-results.json')]:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report['evaluation'],indent=2))
