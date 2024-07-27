import pandas as pd
import os
import glob
import re

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

def load_dir(dir: str) -> pd.DataFrame:
    """
    Loads all `progress.csv` in a test-tune folder.
    
    Args:
        dir: The path to the test-tune folder.
    
    Returns:
        A DataFrame containing all the progress data.
    """
    # Concatenate DFs
    df = pd.concat([pd.read_csv(fname) for fname in glob.glob(f"{dir}/*/progress.csv")])
    return df


def peak_memory_in_dir(dir: str) -> float:
    """
    Return max memory usage (per mega trial) in GB. 
    """
    # regex for Peak memory: 185924KB.
    regex = r"Peak memory: (\d+)KB."
    max_memory = 0
    for path in glob.glob(f"{dir}/*-or/*.log"):
        with open(path) as f:
            matches = re.findall(regex, f.readlines()[-1])
            memory = int(matches[0]) if matches else 0
        max_memory = max(max_memory, memory)
    # Convert KB to GB
    max_memory = max_memory/1000000
    return max_memory

def runtime_in_dir(dir: str) -> float:
    """
    Return runtime and peak runtime
    """
    df = load_dir(dir)
    total_runtime = df["time_total_s"].sum()
    peak_runtime = df["time_total_s"].max()
    return total_runtime, peak_runtime

if __name__ == "__main__":
    design = "ibex"
    platform = "asap7"
    LOG_DIR = os.path.join(CUR_DIR, f'../../../../../flow/logs/{platform}/{design}/')
    # from a dir pick the latest test-tune folder
    path = sorted(os.listdir(LOG_DIR))[-1]
    path = os.path.join(LOG_DIR, path)
    assert len(os.listdir(path)) > 200, f"Should have ~100 trials, only have {len(os.listdir(path))/2}"
    print("Folder:", path)
    # Print 3 decimal places
    print(f"Max Memory (GB): {peak_memory_in_dir(path):.3f}")
    total_runtime, peak_runtime = runtime_in_dir(path)
    print(f"Total runtime: {total_runtime:.3f} s, Peak runtime: {peak_runtime:.3f} s")
 