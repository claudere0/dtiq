import argparse
import csv
import os
from pathlib import Path

MATPLOTLIB_CACHE = Path(".cache/matplotlib").resolve()
MATPLOTLIB_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MATPLOTLIB_CACHE))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description="Plot trade-off curves from metrics.csv.")
    parser.add_argument("--metrics-csv", required=True, help="Path to the CSV created by collect_metrics.py.")
    return parser.parse_args()


def load_rows(path):
    with Path(path).open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        row["dataset_size_mb"] = float(row["dataset_size_mb"])
        row["map50"] = float(row["map50"])
        row["map50_95"] = float(row["map50_95"])
    return rows


def sort_rows(rows):
    return sorted(rows, key=lambda row: row["dataset_size_mb"])


def plot_metric(rows, metric_key, ylabel, output_path):
    plt.figure(figsize=(9, 6))

    groups = {
        "original": [row for row in rows if row["quantization_type"] == "original"],
        "jpeg": sort_rows([row for row in rows if row["quantization_type"] == "jpeg"]),
        "bpc": sort_rows([row for row in rows if row["quantization_type"] == "bpc"]),
    }
    colors = {"original": "#111111", "jpeg": "#d95f02", "bpc": "#1b9e77"}

    for label, group_rows in groups.items():
        if not group_rows:
            continue
        x = [row["dataset_size_mb"] for row in group_rows]
        y = [row[metric_key] for row in group_rows]
        plt.plot(x, y, marker="o", linewidth=2, label=label.upper(), color=colors[label])
        for row in group_rows:
            plt.annotate(
                row["variant"],
                (row["dataset_size_mb"], row[metric_key]),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=9,
            )

    plt.xlabel("Dataset size (MB)")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} vs dataset size")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main():
    args = parse_args()
    rows = load_rows(args.metrics_csv)
    plots_dir = Path(args.metrics_csv).resolve().parent.parent / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    plot_metric(rows, "map50", "mAP50", plots_dir / "map50_vs_size.png")
    plot_metric(rows, "map50_95", "mAP50-95", plots_dir / "map50_95_vs_size.png")
    print(f"Saved plots to {plots_dir}")


if __name__ == "__main__":
    main()
