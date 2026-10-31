"""Read original UCI XLSX and export daily observations, without customer identifiers.
Run with Python containing pandas and openpyxl. No workbook is modified.
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
import pandas as pd

CUTOFF = pd.Timestamp('2011-11-01')
END = pd.Timestamp('2011-12-08')  # Dec 9 is an incomplete trading day.


def prepare(frame, top=10, cutoff=CUTOFF):
    cutoff = pd.Timestamp(cutoff)
    original = len(frame)
    frame = frame.drop_duplicates().copy()
    unique = len(frame)
    frame['StockCode'] = frame.StockCode.astype(str).str.strip()
    frame['InvoiceDate'] = pd.to_datetime(frame.InvoiceDate)
    cancelled = frame.InvoiceNo.astype(str).str.upper().str.startswith('C')
    positive = (frame.Quantity > 0) & (frame.UnitPrice > 0)
    goods = frame.StockCode.str.match(r'^\d{5}[A-Za-z]?$')
    valid = (~cancelled) & positive & goods & frame.InvoiceDate.notna()
    clean = frame[valid].copy()
    clean['date'] = clean.InvoiceDate.dt.normalize()
    clean = clean[clean.date <= END]
    # Selection is based only on data available at the evaluation cutoff.
    selection = clean[clean.date <= cutoff].groupby('StockCode').Quantity.sum()
    selected = selection.sort_values(ascending=False).head(top).index.tolist()
    observations, products = [], []
    for code in selected:
        part = clean[clean.StockCode == code].copy()
        part['revenue'] = part.Quantity * part.UnitPrice
        daily = part.groupby('date').agg(units=('Quantity','sum'), revenue=('revenue','sum'))
        calendar = pd.date_range(daily.index.min(), END, freq='D')
        daily = daily.reindex(calendar)
        prices = (daily.revenue / daily.units).ffill()
        units = daily.units.fillna(0).astype(int)
        cumulative = units.cumsum()
        name = part[part.date <= cutoff].Description.dropna().iloc[-1]
        pid = 'UCI-' + code
        products.append({'id':pid,'title':str(name),'currency':'GBP'})
        for day in calendar:
            observations.append({'product_id':pid,'price':float(prices.loc[day]),
                                 'sold_quantity':int(cumulative.loc[day]),
                                 'daily_units':int(units.loc[day]),
                                 'review_count':0,'score':0,
                                 'data_source':'verified_import',
                                 'captured_at':day.isoformat()})
    return {'source':{'url':'https://archive.ics.uci.edu/dataset/352/online+retail',
                       'doi':'10.24432/C5BW33','author':'Daqing Chen (2015)',
                       'license':'CC BY 4.0','currency':'GBP','historical':True},
            'preparation':{'raw_rows':original,'duplicate_rows_removed':original-unique,
                           'cancelled_rows':int(cancelled.sum()),
                           'rows_excluded_after_deduplication':int((~valid).sum()),
                           'selection_cutoff':str(cutoff.date()),'last_complete_day':str(END.date()),
                           'target':'gross positive units; cancellations and returns excluded',
                           'zero_days':'No eligible sale in a complete transaction log; not a stock-availability claim',
                           'price':'quantity-weighted daily GBP price; forward fill only',
                           'neutral_features':'review_count and score are zero because source lacks them'},
            'products':products,'observations':observations}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',default='work/uci/online-retail.zip')
    parser.add_argument('--output',default='work/uci/prepared.json')
    parser.add_argument('--selection-cutoff', default=str(CUTOFF.date()))
    args=parser.parse_args()
    archive=Path(args.archive)
    with zipfile.ZipFile(archive) as z:
        filename=next(n for n in z.namelist() if n.endswith('.xlsx'))
        with z.open(filename) as f:
            frame=pd.read_excel(f,engine='openpyxl')
    result=prepare(frame, cutoff=args.selection_cutoff)
    result['source']['archive_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest()
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False))
    print(json.dumps({'products':len(result['products']),'observations':len(result['observations']),**result['preparation']},indent=2))
