import argparse
import csv
import os
from pathlib import Path

MATPLOTLIB_CACHE = Path(".cache/matplotlib").resolve()
MATPLOTLIB_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MATPLOTLIB_CACHE))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 14, 'axes.titlesize': 16, 'axes.labelsize': 14, 'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 12})

COLORS = {
    "original": "#222222",
    "jpeg": "#d95f02",
    "bpc": "#1b9e77",
    "png_control": "#6a51a3",
}

MODELS = [
    ("YOLOv8n", "results/val5k_yolov8n/summary/metrics.csv"),
    ("YOLOv8m", "results/val5k_yolov8m/summary/metrics.csv"),
    ("RT-DETR-L", "results/val5k_rtdetr_l/summary/metrics.csv"),
]

def load_metrics_rows(path):
    with Path(path).open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        row["dataset_size_mb"] = float(row["dataset_size_mb"])
        row["map50"] = float(row["map50"])
    return rows

def is_png_control(row):
    return row["variant"] == "b8"

def by_type(rows, quantization_type):
    return [row for row in rows if row["quantization_type"] == quantization_type]

def bpc_quantized_rows(rows):
    return [row for row in rows if row["quantization_type"] == "bpc" and not is_png_control(row)]

def plot_line_group(ax, rows, x_key, y_key, color, label):
    rows = sorted(rows, key=lambda row: row[x_key])
    ax.plot(
        [row[x_key] for row in rows],
        [row[y_key] for row in rows],
        marker="o",
        linewidth=2,
        color=color,
        label=label,
        zorder=3,
    )
    for row in rows:
        ax.annotate(
            row["variant"],
            (row[x_key], row[y_key]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=10,
        )

def plot_model_ax(ax, rows, title):
    plot_line_group(ax, by_type(rows, "original"), "dataset_size_mb", "map50", COLORS["original"], "ORIGINAL")
    plot_line_group(ax, by_type(rows, "jpeg"), "dataset_size_mb", "map50", COLORS["jpeg"], "JPEG")
    plot_line_group(ax, bpc_quantized_rows(rows), "dataset_size_mb", "map50", COLORS["bpc"], "BPC")
    
    control_rows = [row for row in rows if is_png_control(row)]
    if control_rows:
        ax.scatter(
            [row["dataset_size_mb"] for row in control_rows],
            [row["map50"] for row in control_rows],
            s=140,
            facecolors="none",
            edgecolors=COLORS["png_control"],
            linewidths=2,
            marker="D",
            label="PNG control (b8)",
            zorder=4,
        )
        for row in control_rows:
            ax.annotate(row["variant"], (row["dataset_size_mb"], row["map50"]), textcoords="offset points", xytext=(5, 5), fontsize=10)

    ax.set_title(title)
    ax.set_xlabel("Dataset size (MB)")
    ax.set_ylabel("mAP50")
    ax.grid(alpha=0.3)

def plot_all_models_ax(ax, all_data):
    model_styles = [("-", "o"), ("--", "s"), (":", "^")]
    for (model_name, rows), (linestyle, marker) in zip(all_data, model_styles):
        jpeg_rows = sorted(by_type(rows, "jpeg"), key=lambda r: r["dataset_size_mb"])
        bpc_rows = sorted(bpc_quantized_rows(rows), key=lambda r: r["dataset_size_mb"])
        
        ax.plot([r["dataset_size_mb"] for r in jpeg_rows], [r["map50"] for r in jpeg_rows], linestyle=linestyle, marker=marker, color=COLORS["jpeg"], label=f"{model_name} JPEG")
        ax.plot([r["dataset_size_mb"] for r in bpc_rows], [r["map50"] for r in bpc_rows], linestyle=linestyle, marker=marker, color=COLORS["bpc"], label=f"{model_name} BPC")
        
    ax.set_title("All Models Comparison")
    ax.set_xlabel("Dataset size (MB)")
    ax.set_ylabel("mAP50")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=10, loc="lower right")

def main():
    out_dir = Path("article/latex_project/results/article_figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    all_data = []
    
    for i, (name, path) in enumerate(MODELS):
        if Path(path).exists():
            rows = load_metrics_rows(path)
            all_data.append((name, rows))
            plot_model_ax(axes[i], rows, name)
            if i == 0:
                axes[i].legend(fontsize=11)
        else:
            print(f"File not found: {path}")
            
    plot_all_models_ax(axes[3], all_data)
    
    plt.tight_layout()
    out_path = out_dir / "fig_multi_model_grid.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved {out_path}")

if __name__ == "__main__":
    main()
