"""Verify that published metrics and model metadata match the exported cases."""
import json
import unittest
from datetime import date
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / 'work/uci/evaluation-v3.json'
MODEL_PATH = ROOT / 'work/uci/weekly-model-v3.joblib'


@unittest.skipUnless(REPORT_PATH.exists() and MODEL_PATH.exists(), 'Run UCI preparation and v3 training first')
class EvaluationArtifactTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(REPORT_PATH.read_text())
        self.model = joblib.load(MODEL_PATH)

    def test_metrics_are_reproducible_from_cases(self):
        report = self.report
        self.assertEqual(report['version'], 'weekly-residual-v3')
        self.assertEqual(len(report['validation']), 3)
        for split in report['validation']:
            self.assertEqual(len(split['cases']), 40)
            actual = [case['actual'] for case in split['cases']]
            for key, expected in split['mae'].items():
                errors = [abs(real - case['predictions'][key]) for real, case in zip(actual, split['cases'])]
                calculated = sum(errors) / len(errors)
                self.assertAlmostEqual(calculated, expected, places=6)
        comparison = report['comparison']
        self.assertEqual(len(comparison['cases']), 40)
        for case in comparison['cases']:
            span = date.fromisoformat(case['target_end']) - date.fromisoformat(case['origin'])
            self.assertEqual(span.days, 7)
            self.assertGreaterEqual(case['predictions'][report['selected_model']], 0)
        candidates = ['residual_forest', 'residual_boosting']
        expected_model = min(candidates, key=lambda key: report['validation_mae'][key])
        self.assertEqual(report['selected_model'], expected_model)
        expected_method = min(report['labels'], key=lambda key: report['validation_mae'][key])
        self.assertEqual(report['selected_method'], expected_method)

    def test_saved_model_metadata_matches_report(self):
        report = self.report
        model = self.model
        self.assertEqual(model['model_version'], 'weekly-residual-v3')
        self.assertEqual(model['features'], report['features'])
        self.assertEqual(model['trained_through'], model['as_of'][:10])
        self.assertLessEqual(model['trained_through'], model['as_of'][:10])
        self.assertEqual(model['training_pairs'], report['final_training_pairs'])
        self.assertAlmostEqual(model['validation_mae'], report['validation_mae'][report['selected_model']], places=6)
        self.assertAlmostEqual(model['reference_mae'], report['validation_mae']['mean_4_weeks'], places=6)
        self.assertEqual(model['source']['archive_sha256'], report['source']['archive_sha256'])


if __name__ == '__main__':
    unittest.main()
