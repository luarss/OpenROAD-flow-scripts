# Unit tests for autotuner/utils.py and autotuner/distributed.py
import unittest
from unittest import mock
import tempfile
import os
import json
from autotuner import utils
from autotuner import distributed


class TestUtilsUnit(unittest.TestCase):
    def test_write_sdc_creates_file_and_replaces_values(self):
        variables = {"CLK_PERIOD": 1234, "UNCERTAINTY": 0.1, "IO_DELAY": 0.2}
        sdc_original = "set clk_period 2000\nset uncertainty 0.05\nset io_delay 0.1\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = utils.write_sdc(variables, tmpdir, sdc_original, "test.sdc")
            self.assertTrue(os.path.exists(file_path))
            with open(file_path) as f:
                content = f.read()
            self.assertIn("set clk_period 1234", content)
            self.assertIn("set uncertainty 0.1", content)
            self.assertIn("set io_delay 0.2", content)

    def test_write_fast_route_creates_file_and_replaces_values(self):
        variables = {"LAYER_ADJUSTM1": 0.5, "GR_SEED": 42}
        fr_original = "set_global_routing_layer_adjustment M1 1.0\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = utils.write_fast_route(
                variables, tmpdir, "sky130hd", fr_original, "test.tcl"
            )
            self.assertTrue(os.path.exists(file_path))
            with open(file_path) as f:
                content = f.read()
            self.assertIn("set_global_routing_layer_adjustment M1 0.5", content)
            self.assertIn("set_global_routing_random -seed 42", content)

    def test_read_metrics_parses_metrics_json(self):
        metrics = {
            "constraints": {"clocks__details": ["clk 1000"]},
            "floorplan": {"design__instance__utilization": 0.5},
            "detailedroute": {"route__drc_errors": 2, "route__wirelength": 123},
            "finish": {
                "timing__setup__ws": -0.1,
                "power__total": 1.2,
                "design__instance__utilization": 0.6,
                "design__instance__area": 100,
                "design__core__area": 80,
                "design__die__area": 120,
            },
        }
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            json.dump(metrics, tmp)
            tmp.close()
            result = utils.read_metrics(tmp.name)
        self.assertEqual(result["clk_period"], 1000.0)
        self.assertEqual(result["worst_slack"], -0.1)
        self.assertEqual(result["total_power"], 1.2)
        self.assertEqual(result["core_util"], 0.5)
        self.assertEqual(result["final_util"], 0.6)
        self.assertEqual(result["design_area"], 100)
        self.assertEqual(result["core_area"], 80)
        self.assertEqual(result["die_area"], 120)
        self.assertEqual(result["wirelength"], 123)
        self.assertEqual(result["num_drc"], 2)
        os.unlink(tmp.name)


class TestDistributedUnit(unittest.TestCase):
    def setUp(self):
        # --- Global variables ---
        # TODO: Refactor global variables
        distributed.LOCAL_DIR = ""
        distributed.SDC_ORIGINAL = ""
        distributed.FR_ORIGINAL = ""

        # --- args namespace ---
        distributed.args = mock.Mock()
        distributed.args.platform = "asap7"
        distributed.args.design = "gcd"

    def tearDown(self):
        return super().tearDown()

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
        ppa = distributed.PPAImprov()
        ppa.step_ = 1
        metrics = {
            "clk_period": 90,
            "worst_slack": 0,
            "total_power": 8,
            "final_util": 0.4,
            "num_drc": 1,
        }
        score, eff_clk, num_drc = ppa.evaluate(metrics)
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
        score, eff_clk, num_drc = ppa.evaluate(metrics)
        self.assertEqual(score, distributed.ERROR_METRIC)
        self.assertEqual(eff_clk, "-")
        self.assertEqual(num_drc, "-")


if __name__ == "__main__":
    import coverage

    cov = coverage.Coverage()
    cov.start()
    unittest.main(exit=False)
    cov.stop()
    cov.save()
    print("\nCoverage Report:")
    cov.report()
    cov.html_report(directory="cov_html")
    print("HTML coverage report generated in ./cov_html/index.html")
