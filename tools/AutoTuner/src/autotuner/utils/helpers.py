import pandas as pd
import os
import glob

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



if __name__ == "__main__":
    path = "test-tune-2024-07-07-13-45-50"
    path = os.path.join(LOG_DIR, path)
    df = load_dir(path)
    df.to_csv("ray27.csv", index=False)

    path = "test-tune-2024-07-07-13-31-40"
    path = os.path.join(LOG_DIR, path)
    df = load_dir(path)
    df.to_csv("ray28.csv", index=False)

    path = "test-tune-2024-07-07-13-57-06"
    path = os.path.join(LOG_DIR, path)
    df = load_dir(path)
    df.to_csv("ray29.csv", index=False)
