# Unit tests for autotuner/distributed.py
import unittest
from unittest import mock
from autotuner import distributed


class TestDistributedUnit(unittest.TestCase):
    def setUp(self):
        # --- Global variables ---
        distributed.LOCAL_DIR = ""
        distributed.SDC_ORIGINAL = ""
        distributed.FR_ORIGINAL = ""

        # Store original values to restore them later
        self._original_local_dir = distributed.LOCAL_DIR
        self._original_sdc_original = distributed.SDC_ORIGINAL
        self._original_fr_original = distributed.FR_ORIGINAL
        self._original_args = getattr(distributed, "args", None)
        self._original_reference = getattr(distributed, "reference", None)

        distributed.args = mock.Mock()
        distributed.args.platform = "asap7"
        distributed.args.design = "gcd"
        distributed.args.eval = "default"  # Default for evaluate

    def tearDown(self):
        # Restore original values
        distributed.LOCAL_DIR = self._original_local_dir
        distributed.SDC_ORIGINAL = self._original_sdc_original
        distributed.FR_ORIGINAL = self._original_fr_original
        if self._original_args is not None:
            distributed.args = self._original_args
        elif hasattr(distributed, "args"):
            delattr(distributed, "args")

        if self._original_reference is not None:
            distributed.reference = self._original_reference
        elif hasattr(distributed, "reference"):
            delattr(distributed, "reference")

    def test_is_valid_padding(self):
        base = distributed.AutoTunerBase()
        # valid: global >= detail
        config = {
            "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT": 4,
            "CELL_PAD_IN_SITES_DETAIL_PLACEMENT": 2,
        }
        self.assertTrue(base._is_valid_padding(config))
        # invalid: global < detail
        config = {
            "CELL_PAD_IN_SITES_GLOBAL_PLACEMENT": 2,
            "CELL_PAD_IN_SITES_DETAIL_PLACEMENT": 4,
        }
        self.assertFalse(base._is_valid_padding(config))
        # missing keys: should be valid
        config = {"CELL_PAD_IN_SITES_GLOBAL_PLACEMENT": 2}
        self.assertTrue(base._is_valid_padding(config))

    def test_evaluate_default(self):
        base = distributed.AutoTunerBase()
        base.step_ = 1
        distributed.args.eval = "default"  # Ensure eval mode is default
        metrics = {"clk_period": 100, "worst_slack": 10, "num_drc": 2}
        score, eff_clk, num_drc = base.evaluate(metrics)
        self.assertIsInstance(score, (int, float))
        self.assertEqual(eff_clk, 90)
        self.assertEqual(num_drc, 2)
        # error case
        metrics = {"clk_period": 100, "worst_slack": "ERR", "num_drc": 2}
        score, eff_clk, num_drc = base.evaluate(metrics)
        self.assertEqual(score, distributed.ERROR_METRIC)
        self.assertEqual(eff_clk, "-")
        self.assertEqual(num_drc, "-")

    def test_ppa_improv_get_ppa(self):
        # Patch reference in distributed
        distributed.reference = {
            "clk_period": 100,
            "worst_slack": 0,
            "total_power": 10,
            "final_util": 0.5,
        }
        metrics = {
            "clk_period": 90,
            "worst_slack": 0,
            "total_power": 8,
            "final_util": 0.4,
            "num_drc": 1,
        }
        ppa = distributed.PPAImprov.get_ppa(metrics)
        self.assertIsInstance(ppa, (int, float))

    def test_ppa_improv_evaluate(self):
        distributed.reference = {
            "clk_period": 100,
            "worst_slack": 0,
            "total_power": 10,
            "final_util": 0.5,
        }
        distributed.args.eval = "ppa-improv"  # Set eval mode for PPAImprov
        ppa_evaluator = distributed.PPAImprov()
        ppa_evaluator.step_ = 1
        metrics = {
            "clk_period": 90,
            "worst_slack": 0,
            "total_power": 8,
            "final_util": 0.4,
            "num_drc": 1,
        }
        score, eff_clk, num_drc = ppa_evaluator.evaluate(metrics)
        self.assertIsInstance(score, (int, float))
        self.assertIsInstance(eff_clk, (int, float))
        self.assertEqual(num_drc, 1)
        # error case
        metrics = {
            "clk_period": 90,
            "worst_slack": "ERR",
            "total_power": 8,
            "final_util": 0.4,
            "num_drc": 1,
        }
        score, eff_clk, num_drc = ppa_evaluator.evaluate(metrics)
        self.assertEqual(score, distributed.ERROR_METRIC)
        self.assertEqual(eff_clk, "-")
        self.assertEqual(num_drc, "-")


if __name__ == "__main__":
    unittest.main()
