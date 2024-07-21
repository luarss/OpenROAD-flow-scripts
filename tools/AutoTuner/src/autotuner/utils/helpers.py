import pandas as pd
import os
import glob
import re

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(CUR_DIR, '../../../../../flow/logs/asap7/gcd')

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

if __name__ == "__main__":
    path = "test-tune-2024-07-07-13-45-50"
    path = os.path.join(LOG_DIR, path)
    print(f"Max Memory (GB): {peak_memory_in_dir(path)}")
    # df = load_dir(path)
    # df.to_csv("ray27.csv", index=False)

    path = "test-tune-2024-07-07-13-31-40"
    path = os.path.join(LOG_DIR, path)
    print(f"Max Memory (GB): {peak_memory_in_dir(path)}")
    # df = load_dir(path)
    # df.to_csv("ray28.csv", index=False)

    path = "test-tune-2024-07-07-13-57-06"
    path = os.path.join(LOG_DIR, path)
    print(f"Max Memory (GB): {peak_memory_in_dir(path)}")
    # df = load_dir(path)
    # df.to_csv("ray29.csv", index=False)
