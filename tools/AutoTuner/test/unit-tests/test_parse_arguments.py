# Unit tests for autotuner/distributed.py (specifically parse_arguments)
import unittest
from unittest import mock
from autotuner.distributed import (
    parse_arguments,
)  # Assuming parse_arguments is in distributed.py


class TestParseArguments(unittest.TestCase):
    def test_required_args(self):
        # Test required arguments are enforced
        with self.assertRaises(SystemExit):
            with mock.patch("sys.argv", ["prog"]):
                parse_arguments()

        # Test minimum required args
        test_args = [
            "prog",
            "--design",
            "gcd",
            "--platform",
            "sky130hd",
            "--config",
            "config.json",
            "tune",
        ]
        with mock.patch("sys.argv", test_args):
            args = parse_arguments()
            self.assertEqual(args.design, "gcd")
            self.assertEqual(args.platform, "sky130hd")
            self.assertEqual(args.config, "config.json")
            self.assertEqual(args.mode, "tune")

    def test_tune_mode_args(self):
        test_args = [
            "prog",
            "--design",
            "gcd",
            "--platform",
            "sky130hd",
            "--config",
            "config.json",
            "tune",
            "--algorithm",
            "hyperopt",
            "--eval",
            "default",
            "--reference",
            "reference.json",
            "--samples",
            "20",
            "--iterations",
            "5",
        ]

        with mock.patch("sys.argv", test_args):
            args = parse_arguments()
            self.assertEqual(args.algorithm, "hyperopt")
            self.assertEqual(args.eval, "default")
            self.assertEqual(args.samples, 20)
            self.assertEqual(args.iterations, 5)

    def test_ppa_improv_requires_reference(self):
        test_args = [
            "prog",
            "--design",
            "gcd",
            "--platform",
            "sky130hd",
            "--config",
            "config.json",
            "tune",
            "--eval",
            "ppa-improv",
        ]

        with self.assertRaises(SystemExit) as cm:
            with mock.patch("sys.argv", test_args):
                parse_arguments()
        self.assertEqual(cm.exception.code, 7)

    def test_resume_requires_experiment_name(self):
        test_args = [
            "prog",
            "--design",
            "gcd",
            "--platform",
            "sky130hd",
            "--config",
            "config.json",
            "tune",
            "--resume",
        ]

        with self.assertRaises(SystemExit) as cm:
            with mock.patch("sys.argv", test_args):
                parse_arguments()
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
