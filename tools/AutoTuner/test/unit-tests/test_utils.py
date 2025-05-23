# Unit tests for autotuner/utils.py
import unittest
import tempfile
import os
import json
from autotuner import utils


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
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
            json.dump(metrics, tmp)
            tmp_name = tmp.name
        try:
            result = utils.read_metrics(tmp_name)
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
        finally:
            os.unlink(tmp_name)

    def test_read_config_sweep_mode(self):
        config_data = {
            "PARAM1": {"minmax": [1, 10], "step": 2},
            "PARAM2": {"minmax": [0.5, 2.0], "step": 0.1},
        }
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
            json.dump(config_data, tmp)
            tmp_name = tmp.name
        try:
            config, sdc_file, fr_file = utils.read_config(tmp_name, "sweep", "random")
            self.assertEqual(config["PARAM1"], [1, 10, 2])
            self.assertEqual(config["PARAM2"], [0.5, 2.0, 0.1])
            self.assertEqual(sdc_file, "")
            self.assertEqual(fr_file, "")
        finally:
            os.unlink(tmp_name)

    def test_read_config_with_sdc_and_fr_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create SDC file
            sdc_content = "set clk_period 1000\n"
            sdc_path = os.path.join(tmpdir, "test.sdc")
            with open(sdc_path, "w") as f:
                f.write(sdc_content)

            # Create FR file
            fr_content = "set_global_routing_layer_adjustment M1 1.0\n"
            fr_path = os.path.join(tmpdir, "test.tcl")
            with open(fr_path, "w") as f:
                f.write(fr_content)

            config_data = {
                "_SDC_FILE_PATH": "test.sdc",
                "_FR_FILE_PATH": "test.tcl",
                "PARAM1": {"minmax": [1, 5], "step": 1, "type": "int"},
            }

            config_path = os.path.join(tmpdir, "config.json")
            with open(config_path, "w") as f:
                json.dump(config_data, f)

            config, sdc_file, fr_file = utils.read_config(
                config_path, "sweep", "random"
            )
            self.assertEqual(sdc_file, sdc_content)
            self.assertEqual(fr_file, fr_content)

    def test_read_config_invalid_json(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
            tmp.write("invalid json content")
            tmp_name = tmp.name
        try:
            with self.assertRaises(ValueError) as context:
                utils.read_config(tmp_name, "sweep", "random")
            self.assertIn("Invalid JSON file", str(context.exception))
        finally:
            os.unlink(tmp_name)

    def test_read_config_file_not_found(self):
        with self.assertRaises(AssertionError) as context:
            utils.read_config("nonexistent_file.json", "sweep", "random")
        self.assertIn("File nonexistent_file.json not found", str(context.exception))

    def test_read_config_skip_best_result(self):
        config_data = {
            "best_result": {"some": "data"},
            "PARAM1": {"minmax": [1, 5], "step": 1},
        }
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
            json.dump(config_data, tmp)
            tmp_name = tmp.name
        try:
            config, _, _ = utils.read_config(tmp_name, "sweep", "random")
            self.assertNotIn("best_result", config)
            self.assertIn("PARAM1", config)
        finally:
            os.unlink(tmp_name)

    def test_parse_flow_variables_successful_execution(self):
        """Test successful parsing of flow variables"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create flow directory structure
            flow_dir = os.path.join(tmpdir, "flow")
            scripts_dir = os.path.join(flow_dir, "scripts")
            os.makedirs(scripts_dir)

            # Create a mock vars.tcl file
            vars_tcl = os.path.join(flow_dir, "vars.tcl")
            with open(vars_tcl, "w") as f:
                f.write("set ::env(TEST_VAR1) value1\n")
                f.write("set env(TEST_VAR2) value2\n")

            # Create a mock script file
            script_file = os.path.join(scripts_dir, "test.tcl")
            with open(script_file, "w") as f:
                f.write("puts $::env(SCRIPT_VAR)\n")
                f.write("set value $env(ANOTHER_VAR)\n")

            # Mock subprocess.run to simulate successful makefile execution
            with unittest.mock.patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0

                variables = utils.parse_flow_variables(tmpdir, "test_platform")

                # Verify the makefile was called correctly
                mock_run.assert_called_once_with(
                    ["make", "-C", flow_dir, "vars", "PLATFORM=test_platform"],
                    capture_output=True,
                )

                # Check that variables were parsed correctly
                self.assertIn("TEST_VAR1", variables)
                self.assertIn("TEST_VAR2", variables)
                self.assertIn("SCRIPT_VAR", variables)
                self.assertIn("ANOTHER_VAR", variables)

    def test_parse_flow_variables_makefile_failure(self):
        """Test handling of makefile execution failure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            flow_dir = os.path.join(tmpdir, "flow")
            os.makedirs(flow_dir)

            # Mock subprocess.run to simulate makefile failure
            with unittest.mock.patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1

                with self.assertRaises(SystemExit):
                    utils.parse_flow_variables(tmpdir, "test_platform")

    def test_parse_flow_variables_missing_vars_tcl(self):
        """Test handling when vars.tcl is not generated"""
        with tempfile.TemporaryDirectory() as tmpdir:
            flow_dir = os.path.join(tmpdir, "flow")
            os.makedirs(flow_dir)

            # Mock subprocess.run to simulate successful makefile but no vars.tcl
            with unittest.mock.patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0

                with self.assertRaises(SystemExit):
                    utils.parse_flow_variables(tmpdir, "test_platform")

    def test_parse_flow_variables_empty_files(self):
        """Test parsing with empty TCL files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            flow_dir = os.path.join(tmpdir, "flow")
            scripts_dir = os.path.join(flow_dir, "scripts")
            os.makedirs(scripts_dir)

            # Create empty vars.tcl file
            vars_tcl = os.path.join(flow_dir, "vars.tcl")
            with open(vars_tcl, "w") as f:
                pass

            # Create empty script file
            script_file = os.path.join(scripts_dir, "empty.tcl")
            with open(script_file, "w") as f:
                pass

            with unittest.mock.patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0

                variables = utils.parse_flow_variables(tmpdir, "test_platform")

                # Should return empty set for empty files
                self.assertEqual(len(variables), 0)

    def test_parse_flow_variables_complex_patterns(self):
        """Test parsing of various env variable patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            flow_dir = os.path.join(tmpdir, "flow")
            scripts_dir = os.path.join(flow_dir, "scripts")
            os.makedirs(scripts_dir)

            # Create vars.tcl with complex patterns
            vars_tcl = os.path.join(flow_dir, "vars.tcl")
            with open(vars_tcl, "w") as f:
                f.write("set env(SIMPLE_VAR)\n")
                f.write('set ::env(MULTI_LINE_VAR1) "value1\nvalue2"\n')

            with unittest.mock.patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0

                variables = utils.parse_flow_variables(tmpdir, "test_platform")

                # Check that multiline variables are parsed correctly
                self.assertIn("MULTI_LINE_VAR1", variables)
                self.assertIn("SIMPLE_VAR", variables)

    def test_openroad_default_install_path(self):
        """Test openroad function with default install path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock args object
            args = unittest.mock.Mock()
            args.experiment = "test_experiment"
            args.platform = "sky130hd"
            args.design = "gcd"
            args.openroad_threads = 4
            args.timeout = 300

            parameters = "PARAM1=value1 PARAM2=value2"
            flow_variant = "variant1"

            with unittest.mock.patch("autotuner.utils.run_command") as mock_run_command:
                metrics_file = utils.openroad(args, tmpdir, parameters, flow_variant)

                # Check that directories are created
                expected_flow_variant = f"{args.experiment}/{flow_variant}"
                log_path = os.path.join(
                    tmpdir,
                    f"flow/logs/{args.platform}/{args.design}",
                    expected_flow_variant,
                )
                report_path = os.path.join(
                    tmpdir,
                    f"flow/reports/{args.platform}/{args.design}",
                    expected_flow_variant,
                )
                results_path = os.path.join(
                    tmpdir,
                    f"flow/results/{args.platform}/{args.design}",
                    expected_flow_variant,
                )

                self.assertTrue(os.path.exists(log_path))
                self.assertTrue(os.path.exists(report_path))
                self.assertTrue(os.path.exists(results_path))

                # Check return value
                expected_metrics_file = os.path.join(log_path, "metrics.json")
                self.assertEqual(metrics_file, os.path.abspath(expected_metrics_file))

                # Verify run_command was called twice (make and metrics)
                self.assertEqual(mock_run_command.call_count, 2)

    def test_openroad_custom_install_path(self):
        """Test openroad function with custom install path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_install = "/custom/install/path"

            args = unittest.mock.Mock()
            args.experiment = "custom_exp"
            args.platform = "asap7"
            args.design = "adder"
            args.openroad_threads = 8
            args.timeout = 600

            with unittest.mock.patch("autotuner.utils.run_command") as mock_run_command:
                utils.openroad(args, tmpdir, "TEST=1", "v1", custom_install)

                # Check that custom install path is used in commands
                make_call = mock_run_command.call_args_list[0]
                make_command = make_call[0][1]  # Second argument is the command
                self.assertIn(
                    f"export PATH={custom_install}/OpenROAD/bin", make_command
                )
                self.assertIn(f":{custom_install}/yosys/bin:$PATH", make_command)

    def test_openroad_command_construction(self):
        """Test that openroad constructs commands correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            args = unittest.mock.Mock()
            args.experiment = "exp1"
            args.platform = "nangate45"
            args.design = "test_design"
            args.openroad_threads = 2
            args.timeout = 120

            parameters = "CLK_PERIOD=1000 CORE_UTIL=50"
            flow_variant = "test_variant"

            with unittest.mock.patch("autotuner.utils.run_command") as mock_run_command:
                utils.openroad(args, tmpdir, parameters, flow_variant)

                # Check make command construction
                make_call = mock_run_command.call_args_list[0]
                make_command = make_call[0][1]

                self.assertIn(f"make -C {tmpdir}/flow", make_command)
                self.assertIn(
                    f"DESIGN_CONFIG=designs/{args.platform}/{args.design}/config.mk",
                    make_command,
                )
                self.assertIn(f"PLATFORM={args.platform}", make_command)
                self.assertIn(
                    f"FLOW_VARIANT={args.experiment}/{flow_variant}", make_command
                )
                self.assertIn(parameters, make_command)
                self.assertIn("EQUIVALENCE_CHECK=0", make_command)
                self.assertIn(f"NUM_CORES={args.openroad_threads}", make_command)
                self.assertIn("SHELL=bash", make_command)

                # Check metrics command construction
                metrics_call = mock_run_command.call_args_list[1]
                metrics_command = metrics_call[0][1]

                self.assertIn(f"{tmpdir}/flow/util/genMetrics.py -x", metrics_command)
                self.assertIn(f"-v {args.experiment}/{flow_variant}", metrics_command)
                self.assertIn(f"-d {args.design}", metrics_command)
                self.assertIn(f"-p {args.platform}", metrics_command)

    def test_openroad_file_paths(self):
        """Test that openroad sets up correct file paths for logging"""
        with tempfile.TemporaryDirectory() as tmpdir:
            args = unittest.mock.Mock()
            args.experiment = "path_test"
            args.platform = "test_platform"
            args.design = "test_design"
            args.openroad_threads = 1
            args.timeout = 60

            with unittest.mock.patch("autotuner.utils.run_command") as mock_run_command:
                utils.openroad(args, tmpdir, "", "variant")

                # Check make command file paths
                make_call = mock_run_command.call_args_list[0]
                make_kwargs = make_call[1]

                expected_log_path = os.path.join(
                    tmpdir, f"flow/logs/{args.platform}/{args.design}/path_test/variant"
                )
                self.assertEqual(
                    make_kwargs["stderr_file"],
                    os.path.join(expected_log_path, "error-make-finish.log"),
                )
                self.assertEqual(
                    make_kwargs["stdout_file"],
                    os.path.join(expected_log_path, "make-finish-stdout.log"),
                )
                self.assertEqual(make_kwargs["timeout"], args.timeout)

                # Check metrics command file paths
                metrics_call = mock_run_command.call_args_list[1]
                metrics_kwargs = metrics_call[1]

                self.assertEqual(
                    metrics_kwargs["stderr_file"],
                    os.path.join(expected_log_path, "error-metrics.log"),
                )
                self.assertEqual(
                    metrics_kwargs["stdout_file"],
                    os.path.join(expected_log_path, "metrics-stdout.log"),
                )

    def test_openroad_directory_creation(self):
        """Test that openroad creates necessary directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            args = unittest.mock.Mock()
            args.experiment = "dir_test"
            args.platform = "platform1"
            args.design = "design1"
            args.openroad_threads = 1
            args.timeout = 30

            # Ensure directories don't exist initially
            flow_variant = f"{args.experiment}/variant1"
            log_path = os.path.join(
                tmpdir, f"flow/logs/{args.platform}/{args.design}", flow_variant
            )
            report_path = os.path.join(
                tmpdir, f"flow/reports/{args.platform}/{args.design}", flow_variant
            )
            results_path = os.path.join(
                tmpdir, f"flow/results/{args.platform}/{args.design}", flow_variant
            )

            self.assertFalse(os.path.exists(log_path))
            self.assertFalse(os.path.exists(report_path))
            self.assertFalse(os.path.exists(results_path))

            with unittest.mock.patch("autotuner.utils.run_command"):
                utils.openroad(args, tmpdir, "", "variant1")

                # Check directories are created
                self.assertTrue(os.path.exists(log_path))
                self.assertTrue(os.path.exists(report_path))
                self.assertTrue(os.path.exists(results_path))

    def test_openroad_empty_parameters(self):
        """Test openroad function with empty parameters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            args = unittest.mock.Mock()
            args.experiment = "empty_test"
            args.platform = "test"
            args.design = "test"
            args.openroad_threads = 1
            args.timeout = 10

            with unittest.mock.patch("autotuner.utils.run_command") as mock_run_command:
                metrics_file = utils.openroad(args, tmpdir, "", "variant")

                # Should still work with empty parameters
                self.assertTrue(metrics_file.endswith("metrics.json"))
                self.assertEqual(mock_run_command.call_count, 2)

                # Check that empty parameters don't break command construction
                make_call = mock_run_command.call_args_list[0]
                make_command = make_call[0][1]
                self.assertIn("FLOW_VARIANT=empty_test/variant ", make_command)


if __name__ == "__main__":
    unittest.main()
