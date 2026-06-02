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


def pareto_optimal(rows):
    tradeoff_rows = [row for row in rows if row["quantization_type"] != "original"]
    frontier = []
    best_map = -1.0
    for row in sorted(tradeoff_rows, key=lambda item: item["dataset_size_mb"]):
        if row["map50"] > best_map:
            frontier.append(row)
            best_map = row["map50"]
    return frontier


def plot_pareto_frontier(rows, output_path):
    tradeoff_rows = [row for row in rows if row["quantization_type"] != "original"]
    groups = {
        "jpeg": [row for row in tradeoff_rows if row["quantization_type"] == "jpeg"],
        "bpc": [row for row in tradeoff_rows if row["quantization_type"] == "bpc"],
    }
    colors = {"jpeg": "#d95f02", "bpc": "#1b9e77"}

    plt.figure(figsize=(9, 6))
    for label, group_rows in groups.items():
        if not group_rows:
            continue
        plt.scatter(
            [row["dataset_size_mb"] for row in group_rows],
            [row["map50"] for row in group_rows],
            s=70,
            color=colors[label],
            label=label.upper(),
            zorder=3,
        )
        for row in group_rows:
            plt.annotate(
                row["variant"],
                (row["dataset_size_mb"], row["map50"]),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=9,
            )

    frontier = pareto_optimal(rows)
    frontier = sorted(frontier, key=lambda row: row["dataset_size_mb"])
    plt.plot(
        [row["dataset_size_mb"] for row in frontier],
        [row["map50"] for row in frontier],
        linestyle="--",
        color="#444444",
        linewidth=2,
        label="Pareto frontier",
        zorder=2,
    )

    plt.xlabel("Dataset size (MB)")
    plt.ylabel("mAP50")
    plt.title("Storage-detection Pareto frontier")
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
    article_figures_dir = Path(args.metrics_csv).resolve().parent.parent.parent / "article_figures"
    article_figures_dir.mkdir(parents=True, exist_ok=True)

    plot_metric(rows, "map50", "mAP50", plots_dir / "map50_vs_size.png")
    plot_metric(rows, "map50_95", "mAP50-95", plots_dir / "map50_95_vs_size.png")
    plot_pareto_frontier(rows, article_figures_dir / "fig8_pareto_storage_map50.png")
    print(f"Saved plots to {plots_dir}")
    print(f"Saved Pareto figure to {article_figures_dir}")


if __name__ == "__main__":
    main()
