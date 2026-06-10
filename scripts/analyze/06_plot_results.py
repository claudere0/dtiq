import argparse
import csv
import os
from pathlib import Path

MATPLOTLIB_CACHE = Path(".cache/matplotlib").resolve()
MATPLOTLIB_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MATPLOTLIB_CACHE))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTICLE_FIGURES_DIR = REPO_ROOT / "article/latex_project/results/article_figures"
PNG_CONTROL_VARIANT = "b8"

COLORS = {
    "original": "#222222",
    "jpeg": "#d95f02",
    "bpc": "#1b9e77",
    "png_control": "#6a51a3",
    "map50": "#7570b3",
    "map50_95": "#66a61e",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Plot val5k curves and export LaTeX PNG figures.")
    parser.add_argument("--metrics-csv", required=True, help="Path to metrics.csv.")
    parser.add_argument(
        "--image-quality-csv",
        default="results/val5k/summary/image_quality.csv",
        help="Path to image_quality.csv for PSNR/SSIM figures.",
    )
    parser.add_argument(
        "--article-figures-dir",
        default=str(DEFAULT_ARTICLE_FIGURES_DIR),
        help="Directory for article PNG figures used by LaTeX.",
    )
    return parser.parse_args()


def load_metrics_rows(path):
    with Path(path).open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        row["dataset_size_mb"] = float(row["dataset_size_mb"])
        row["map50"] = float(row["map50"])
        row["map50_95"] = float(row["map50_95"])
        row["precision"] = float(row["precision"])
        row["recall"] = float(row["recall"])
    return rows


def load_quality_rows(path):
    if not Path(path).exists():
        return {}
    with Path(path).open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    quality = {}
    for row in rows:
        psnr = row["mean_psnr"].strip()
        ssim = row["mean_ssim"].strip()
        quality[row["variant"]] = {
            "psnr": float(psnr) if psnr else None,
            "ssim": float(ssim) if ssim else None,
        }
    return quality


def is_png_control(row):
    return row["variant"] == PNG_CONTROL_VARIANT


def by_type(rows, quantization_type):
    return [row for row in rows if row["quantization_type"] == quantization_type]


def bpc_quantized_rows(rows):
    return [row for row in rows if row["quantization_type"] == "bpc" and not is_png_control(row)]


def png_control_rows(rows):
    return [row for row in rows if is_png_control(row)]


def bar_color(row):
    if is_png_control(row):
        return COLORS["png_control"]
    return COLORS.get(row["quantization_type"], COLORS["bpc"])


def annotate_points(rows, x_key, y_key):
    for row in rows:
        plt.annotate(
            row["variant"],
            (row[x_key], row[y_key]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )


def plot_control_markers(rows, x_key, y_key):
    plt.scatter(
        [row[x_key] for row in rows],
        [row[y_key] for row in rows],
        s=140,
        facecolors="none",
        edgecolors=COLORS["png_control"],
        linewidths=2,
        marker="D",
        label="PNG control (b8)",
        zorder=4,
    )
    annotate_points(rows, x_key, y_key)


def plot_line_group(rows, x_key, y_key, color, label):
    rows = sorted(rows, key=lambda row: row[x_key])
    plt.plot(
        [row[x_key] for row in rows],
        [row[y_key] for row in rows],
        marker="o",
        linewidth=2,
        color=color,
        label=label,
        zorder=3,
    )
    annotate_points(rows, x_key, y_key)


def plot_metric(rows, metric_key, ylabel, output_path):
    plt.figure(figsize=(9, 6))
    plot_line_group(by_type(rows, "original"), "dataset_size_mb", metric_key, COLORS["original"], "ORIGINAL")
    plot_line_group(by_type(rows, "jpeg"), "dataset_size_mb", metric_key, COLORS["jpeg"], "JPEG")
    plot_line_group(bpc_quantized_rows(rows), "dataset_size_mb", metric_key, COLORS["bpc"], "BPC")
    control_rows = png_control_rows(rows)
    if control_rows:
        plot_control_markers(control_rows, "dataset_size_mb", metric_key)
    plt.xlabel("Dataset size (MB)")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} vs dataset size")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_compression_chart(rows, y_key, title, ylabel, output_path):
    plt.figure(figsize=(9, 6))
    baseline_size = next(row for row in rows if row["quantization_type"] == "original")["dataset_size_mb"]
    tradeoff_rows = [row for row in rows if row["quantization_type"] != "original" and not is_png_control(row)]
    for row in tradeoff_rows:
        row["compression_ratio"] = baseline_size / row["dataset_size_mb"]
        if y_key == "map50_drop_pct":
            baseline_map = next(r for r in rows if r["quantization_type"] == "original")["map50"]
            row["map50_drop_pct"] = ((baseline_map - row["map50"]) / baseline_map) * 100.0

    plot_line_group(by_type(tradeoff_rows, "jpeg"), "compression_ratio", y_key, COLORS["jpeg"], "JPEG")
    plot_line_group(bpc_quantized_rows(tradeoff_rows), "compression_ratio", y_key, COLORS["bpc"], "BPC")
    plt.xlabel("Compression ratio vs original")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_size_bars(rows, output_path):
    ordered = sorted(rows, key=lambda row: row["dataset_size_mb"])
    plt.figure(figsize=(12, 6))
    plt.bar(
        [row["variant"] for row in ordered],
        [row["dataset_size_mb"] for row in ordered],
        color=[bar_color(row) for row in ordered],
    )
    plt.ylabel("Dataset size (MB)")
    plt.title("Dataset size by variant")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_detection_bars(rows, output_path):
    ordered_names = [
        "original",
        "q94",
        "q88",
        "q75",
        "q50",
        "q25",
        "b8",
        "b7",
        "b4",
        "b3",
        "b2",
        "b1",
    ]
    row_map = {row["variant"]: row for row in rows}
    ordered = [row_map[name] for name in ordered_names if name in row_map]
    labels = [row["variant"] for row in ordered]
    x = list(range(len(ordered)))
    width = 0.35

    plt.figure(figsize=(12, 6))
    plt.bar(
        [value - width / 2 for value in x],
        [row["map50"] for row in ordered],
        width=width,
        label="mAP50",
        color=COLORS["map50"],
    )
    plt.bar(
        [value + width / 2 for value in x],
        [row["map50_95"] for row in ordered],
        width=width,
        label="mAP50-95",
        color=COLORS["map50_95"],
    )
    for index, row in enumerate(ordered):
        if is_png_control(row):
            plt.axvspan(index - 0.5, index + 0.5, color=COLORS["png_control"], alpha=0.08, zorder=0)
    plt.xticks(x, labels, rotation=45, ha="right")
    plt.ylabel("Detection metric")
    plt.title("Detection metrics by variant")
    plt.grid(axis="y", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_quality_scatter(rows, quality, metric_key, xlabel, title, output_path):
    points = []
    for row in rows:
        if row["quantization_type"] == "original" or is_png_control(row):
            continue
        value = quality.get(row["variant"], {}).get(metric_key)
        if value is None:
            continue
        points.append((row, value))

    plt.figure(figsize=(9, 6))
    jpeg_rows = [row for row, _ in points if row["quantization_type"] == "jpeg"]
    bpc_rows = [row for row, _ in points if row["quantization_type"] == "bpc"]
    if jpeg_rows:
        plt.scatter(
            [quality[row["variant"]][metric_key] for row in jpeg_rows],
            [row["map50"] for row in jpeg_rows],
            s=70,
            color=COLORS["jpeg"],
            label="JPEG",
        )
        for row in jpeg_rows:
            plt.annotate(
                row["variant"],
                (quality[row["variant"]][metric_key], row["map50"]),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=9,
            )
    if bpc_rows:
        plt.scatter(
            [quality[row["variant"]][metric_key] for row in bpc_rows],
            [row["map50"] for row in bpc_rows],
            s=70,
            color=COLORS["bpc"],
            label="BPC",
        )
        for row in bpc_rows:
            plt.annotate(
                row["variant"],
                (quality[row["variant"]][metric_key], row["map50"]),
                textcoords="offset points",
                xytext=(5, 5),
                fontsize=9,
            )
    plt.xlabel(xlabel)
    plt.ylabel("mAP50")
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def pareto_optimal(rows):
    frontier = []
    best_map = -1.0
    for row in sorted(rows, key=lambda item: item["dataset_size_mb"]):
        if row["map50"] > best_map:
            frontier.append(row)
            best_map = row["map50"]
    return frontier


def plot_pareto_frontier(rows, output_path):
    tradeoff_rows = [row for row in rows if row["quantization_type"] != "original"]
    pareto_rows = [row for row in tradeoff_rows if not is_png_control(row)]

    plt.figure(figsize=(9, 6))
    jpeg_rows = by_type(tradeoff_rows, "jpeg")
    bpc_rows = bpc_quantized_rows(tradeoff_rows)
    if jpeg_rows:
        plt.scatter(
            [row["dataset_size_mb"] for row in jpeg_rows],
            [row["map50"] for row in jpeg_rows],
            s=70,
            color=COLORS["jpeg"],
            label="JPEG",
            zorder=3,
        )
        annotate_points(jpeg_rows, "dataset_size_mb", "map50")
    if bpc_rows:
        plt.scatter(
            [row["dataset_size_mb"] for row in bpc_rows],
            [row["map50"] for row in bpc_rows],
            s=70,
            color=COLORS["bpc"],
            label="BPC",
            zorder=3,
        )
        annotate_points(bpc_rows, "dataset_size_mb", "map50")
    control_rows = png_control_rows(tradeoff_rows)
    if control_rows:
        plot_control_markers(control_rows, "dataset_size_mb", "map50")

    frontier = pareto_optimal(pareto_rows)
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


def export_article_pngs(rows, quality, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_metric(rows, "map50", "mAP50", output_dir / "fig1_map50_vs_size.png")
    plot_compression_chart(
        rows,
        "map50",
        "Compression ratio vs detection quality",
        "mAP50",
        output_dir / "fig2_compression_ratio_vs_map50.png",
    )
    plot_compression_chart(
        rows,
        "map50_drop_pct",
        "Detection loss under compression",
        "Relative mAP50 drop (%)",
        output_dir / "fig3_relative_map50_drop.png",
    )
    plot_size_bars(rows, output_dir / "fig4_dataset_size_bars.png")
    plot_detection_bars(rows, output_dir / "fig5_detection_metric_bars.png")
    if quality:
        plot_quality_scatter(
            rows,
            quality,
            "psnr",
            "Mean PSNR",
            "PSNR vs detection quality",
            output_dir / "fig6_psnr_vs_map50.png",
        )
        plot_quality_scatter(
            rows,
            quality,
            "ssim",
            "Mean SSIM",
            "SSIM vs detection quality",
            output_dir / "fig7_ssim_vs_map50.png",
        )
    plot_pareto_frontier(rows, output_dir / "fig10_pareto_storage_map50.png")


def main():
    args = parse_args()
    rows = load_metrics_rows(args.metrics_csv)
    quality = load_quality_rows(args.image_quality_csv)
    plots_dir = Path(args.metrics_csv).resolve().parent.parent / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    plot_metric(rows, "map50", "mAP50", plots_dir / "map50_vs_size.png")
    plot_metric(rows, "map50_95", "mAP50-95", plots_dir / "map50_95_vs_size.png")
    export_article_pngs(rows, quality, args.article_figures_dir)
    print(f"Saved exploratory plots to {plots_dir}")
    print(f"Saved article PNG figures to {args.article_figures_dir}")


if __name__ == "__main__":
    main()
