import unittest
import subprocess
import os
import json
import pandas as pd
import glob

cur_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(cur_dir, "../src/autotuner")
os.chdir(src_dir)


def get_latest_date(path):
    return max(glob.glob(f"{path}/*"), key=os.path.getmtime)

def combine_csv(path):
    df = pd.concat([pd.read_csv(fname) for fname in glob.glob(f"{path}/*/progress.csv")])
    df.to_csv(f"{path}/progress_overall.csv", index=False)

def load_df(filename):
    df = pd.read_csv(filename)
    cols_to_remove = [
        "done", "training_iteration", "trial_id", "date",
        "timestamp", "pid", "hostname", "node_ip", "time_since_restore",
        "time_total_s", "iterations_since_restore",
    ]    
    df = df[df['minimum'] != 9e99]
    df = df.drop(columns=cols_to_remove)
    return df

def get_latest_data(path):
    latest_path = get_latest_date(path)
    print("Using folder:", latest_path)
    combine_csv(latest_path)
    return load_df(f"{latest_path}/progress_overall.csv")

class BaseTuneRegressionBaseTest(unittest.TestCase):
    platform = ""
    design = ""
    qor = 0
    THRESHOLD = 0.05 # qor mean is within +- 5% of the expected value

    def setUp(self):
        self.config = os.path.join(
            cur_dir,
            f"../../../flow/designs/{self.platform}/{self.design}/autotuner.json",
        )
        self.experiment = f"test-regression"
        self.command = (
            "python3 distributed.py"
            f" --design {self.design}"
            f" --platform {self.platform}"
            f" --experiment {self.experiment}"
            f" --config {self.config}"
            f" tune --samples 10"
        )


class ASAP7TuneRegressionBaseTest(BaseTuneRegressionBaseTest):
    platform = "asap7"
    design = "gcd"
    qor = 37668.290

    def test_tune(self):
        out = subprocess.run(self.command, shell=True, check=True)
        successful = out.returncode == 0
        self.assertTrue(successful)

        # check if final mean QoR is within confidence interval of expected value
        df = get_latest_data(f"../../../../flow/logs/{self.platform}/{self.design}")
        mean_qor = df["minimum"].mean()
        self.assertLess(abs(mean_qor - self.qor) / self.qor, (1-self.THRESHOLD))


class SKY130HDTuneRegressionBaseTest(BaseTuneRegressionBaseTest):
    platform = "sky130hd"
    design = "gcd"
    qor = 327.023

    def test_tune(self):
        out = subprocess.run(self.command, shell=True, check=True)
        successful = out.returncode == 0
        self.assertTrue(successful)

        # check if final mean QoR is within confidence interval of expected value
        df = get_latest_data(f"../../../../flow/logs/{self.platform}/{self.design}")
        mean_qor = df["minimum"].mean()
        self.assertLess(abs(mean_qor - self.qor) / self.qor, (1-self.THRESHOLD))


class IHPSG13G2TuneRegressionBaseTest(BaseTuneRegressionBaseTest):
    platform = "ihp-sg13g2"
    design = "gcd"
    qor = 251.102

    def test_tune(self):
        out = subprocess.run(self.command, shell=True, check=True)
        successful = out.returncode == 0
        self.assertTrue(successful)

        # check if final mean QoR is within confidence interval of expected value
        df = get_latest_data(f"../../../../flow/logs/{self.platform}/{self.design}")
        mean_qor = df["minimum"].mean()
        self.assertLess(abs(mean_qor - self.qor) / self.qor, (1-self.THRESHOLD))

if __name__ == "__main__":
    unittest.main()
