import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from train_uci_v2 import make_features, split, FEATURES


def records():
    result = []
    for pid in ['A', 'B']:
        total = 0
        for i, date in enumerate(pd.date_range('2011-01-01', periods=100)):
            units = (i % 7) + 1
            total += units
            result.append(dict(product_id=pid, captured_at=date.isoformat(),
                               daily_units=units, sold_quantity=total, price=10,
                               review_count=0, score=0))
    return result


class V2Tests(unittest.TestCase):
    def test_future_changes_do_not_change_features(self):
        original = records()
        train, _ = make_features(original)
        changed = [dict(r) for r in original]
        for r in changed:
            if pd.Timestamp(r['captured_at']) > pd.Timestamp('2011-02-15'):
                r['price'] = 1000
                # A later one-off sale changes future targets, never current inputs.
                r['sold_quantity'] += 100
                if r['captured_at'].startswith('2011-02-16'):
                    r['daily_units'] += 100
        altered, _ = make_features(changed)
        a = train[train.captured_at <= '2011-02-15'][FEATURES]
        b = altered[altered.captured_at <= '2011-02-15'][FEATURES]
        pd.testing.assert_frame_equal(a, b)

    def test_target_and_lags_are_seven_calendar_days(self):
        frame, latest = make_features(records())
        self.assertTrue((frame.target == 28).all())
        self.assertTrue((frame.sales_7 == 28).all())
        self.assertTrue((frame.sales_28 == 112).all())
        self.assertEqual(len(latest), 2)
        self.assertTrue(latest.target.isna().all())

    def test_missing_and_duplicate_days_rejected(self):
        data = records()
        with self.assertRaises(ValueError):
            make_features(data[1:20]+data[21:])
        with self.assertRaises(ValueError):
            make_features(data+[data[0]])

    def test_splits_keep_products_on_shared_dates_and_purge_targets(self):
        frame, _ = make_features(records())
        train, test = split(frame, '2011-03-01')
        self.assertLessEqual(train.target_at.max(), test.captured_at.min())
        self.assertEqual(len(test), 8)
        self.assertTrue((test.groupby('captured_at').product_id.nunique() == 2).all())

if __name__ == '__main__':
    unittest.main()
