import glob
import pandas as pd
import matplotlib.pyplot as plt


def load_dir(dir: str) -> pd.DataFrame:
    # Concatenate DFs
    df = pd.concat([pd.read_csv(fname) for fname in glob.glob(f"{dir}/*/progress.csv")])
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    cols_to_remove = [
        "done",
        "training_iteration",
        "trial_id",
        "date",
        "pid",
        "hostname",
        "node_ip",
        "time_since_restore",
        "time_total_s",
        "iterations_since_restore",
    ]
    df = df.drop(columns=cols_to_remove)
    df = df[df["minimum"] != 9e99]
    df["timestamp"] -= df["timestamp"].min()
    return df


def plot_qor(df: pd.DataFrame):
    # Plots: Boxplot and time series plot for QoR and runtime
    fig, ax = plt.subplots(2, figsize=(15, 10))
    ax[0].scatter(df["timestamp"], df["minimum"])
    ax[0].set_xlabel("Time (s)")
    ax[0].set_ylabel("QoR")
    ax[0].set_title("QoR vs Time")

    ax[1].scatter(df["timestamp"], df["time_this_iter_s"])
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("Trial runtime (s)")
    plt.savefig("images/qor.png")

    plt.figure(figsize=(15, 10))
    plt.boxplot(df["minimum"])
    plt.ylabel("QoR")
    plt.title("QoR Boxplot")
    plt.savefig("images/qor-boxplot.png")


def plot(df: pd.DataFrame, metric: str):
    assert metric in ["qor", "period", "worst_slack"]
    if metric == "qor":
        plot_qor(df)
    elif metric == "period":
        # plot_period(df)
        pass
    elif metric == "worst_slack":
        # plot_worst_slack(df)
        pass


def main(results_dir: str):
    df = load_dir(results_dir)
    df = preprocess(df)
    plot(df, "qor")
    plot(df, "period")
    # plot(df, "worst_slack")


if __name__ == "__main__":
    main("../../../../../flow/logs/asap7/gcd/test-tune-2024-09-17-12-00-44")
