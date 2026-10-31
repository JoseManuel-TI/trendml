import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from train_uci_v3 import make_features, predict_residual, FEATURES
from train_uci_v2 import split
from test_uci_v2 import records

class ZeroCorrection:
    def predict(self, features):
        return np.zeros(len(features))

class NegativeCorrection:
    def predict(self, features):
        return np.full(len(features), -1000)

class ResidualTests(unittest.TestCase):
    def test_zero_correction_recovers_baseline_without_target(self):
        _, latest = make_features(records())
        latest = latest.drop(columns=['target', 'target_at'])
        np.testing.assert_allclose(predict_residual(ZeroCorrection(), latest), latest.sales_28/4)
        self.assertTrue((predict_residual(NegativeCorrection(), latest) == 0).all())

    def test_future_sales_do_not_change_inputs(self):
        data = records()
        first, _ = make_features(data)
        changed = [dict(r) for r in data]
        for row in changed:
            if pd.Timestamp(row['captured_at']) > pd.Timestamp('2011-03-01'):
                row['sold_quantity'] += 100
                row['price'] = 300
                if row['captured_at'].startswith('2011-03-02'):
                    row['daily_units'] += 100
        second, _ = make_features(changed)
        pd.testing.assert_frame_equal(first[first.captured_at <= '2011-03-01'][FEATURES],
                                      second[second.captured_at <= '2011-03-01'][FEATURES])

    def test_full_history_and_shared_temporal_split(self):
        frame, latest = make_features(records())
        self.assertTrue((frame.mean_week_56 == 28).all())
        self.assertTrue((frame.zero_fraction_56 == 0).all())
        self.assertEqual(frame.captured_at.min(), pd.Timestamp('2011-02-25'))
        # A cutoff must leave a full week of known targets after warm-up.
        train, test = split(frame, '2011-03-06')
        self.assertLessEqual(train.target_at.max(), test.captured_at.min())
        self.assertEqual(len(test), 8)
        self.assertEqual(len(latest), 2)
        self.assertTrue(latest.target.isna().all())

if __name__ == '__main__':
    unittest.main()
