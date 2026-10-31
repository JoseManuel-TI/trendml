"""Read-only SQLite audit. No credentials or user records are printed."""
import argparse
import json
import sqlite3
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('database', nargs='?', default='backend/trendml.db')
args = parser.parse_args()
path = Path(args.database).resolve()
with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
    total, products, demo, first, last = db.execute("""
        SELECT count(*), count(distinct product_id),
               coalesce(sum(CASE WHEN product_id LIKE 'DEMO-%' THEN 1 ELSE 0 END),0),
               min(captured_at), max(captured_at) FROM price_history
    """).fetchone()
    columns = {r[1] for r in db.execute('PRAGMA table_info(price_history)')}
    sources = (dict(db.execute('SELECT data_source,count(*) FROM price_history GROUP BY data_source').fetchall())
               if 'data_source' in columns else {'unrecorded': total})
print(json.dumps({'observations':total, 'products':products, 'demo_observations':demo,
                  'first':first, 'last':last, 'sources':sources,
                  'provenance_verified':False if 'unrecorded' in sources else None}, indent=2))
