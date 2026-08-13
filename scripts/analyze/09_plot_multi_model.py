import argparse
import csv
import os
from pathlib import Path

MATPLOTLIB_CACHE = Path(".cache/matplotlib").resolve()
MATPLOTLIB_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MATPLOTLIB_CACHE))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 16,
    'axes.titlesize': 18,
    'axes.titleweight': 'bold',
    'axes.labelsize': 17,
    'axes.labelweight': 'bold',
    'xtick.labelsize': 15,
    'ytick.labelsize': 15,
    'legend.fontsize': 14,
    'figure.titlesize': 20,
    'figure.titleweight': 'bold'
})

MODEL_STYLES = {
    "YOLOv8n": {"marker": "D", "linestyle": "-", "jpeg": "#9671bd", "bpc": "#6a408d"},
    "YOLOv8m": {"marker": "s", "linestyle": "--", "jpeg": "#77b5b6", "bpc": "#378d94"},
    "RT-DETR-L": {"marker": "o", "linestyle": ":", "jpeg": "#f2ad73", "bpc": "#c45a16"}
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

def plot_line_group(ax, rows, x_key, y_key, color, label, marker="o"):
    rows = sorted(rows, key=lambda row: row[x_key])
    ax.plot(
        [row[x_key] for row in rows],
        [row[y_key] for row in rows],
        marker=marker,
        linewidth=2,
        color=color,
        label=label,
        zorder=3,
        markeredgecolor='white',
        markeredgewidth=0.5
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
    style = MODEL_STYLES[title]
    marker = style["marker"]
    
    plot_line_group(ax, by_type(rows, "original"), "dataset_size_mb", "map50", "#7e7e7e", "ORIGINAL", marker=marker)
    plot_line_group(ax, by_type(rows, "jpeg"), "dataset_size_mb", "map50", style["jpeg"], "JPEG", marker=marker)
    plot_line_group(ax, bpc_quantized_rows(rows), "dataset_size_mb", "map50", style["bpc"], "BPC", marker=marker)
    
    control_rows = [row for row in rows if is_png_control(row)]
    if control_rows:
        ax.scatter(
            [row["dataset_size_mb"] for row in control_rows],
            [row["map50"] for row in control_rows],
            s=140,
            facecolors="none",
            edgecolors="#333333",
            linewidths=2,
            marker=marker,
            label="PNG control (b8)",
            zorder=4,
        )
        for row in control_rows:
            ax.annotate(row["variant"], (row["dataset_size_mb"], row["map50"]), textcoords="offset points", xytext=(5, 5), fontsize=10)

    ax.set_title(title, pad=15)
    ax.set_xlabel("Dataset size (MB)", labelpad=10)
    ax.set_ylabel("mAP50", labelpad=10)
    
    ax.set_axisbelow(True)
    ax.minorticks_on()
    ax.grid(True, which='major', linestyle='-', linewidth=0.75, alpha=0.3)
    ax.grid(True, which='minor', linestyle='-', linewidth=0.25, alpha=0.15)

def plot_all_models_ax(ax, all_data):
    for model_name, rows in all_data:
        style = MODEL_STYLES[model_name]
        jpeg_rows = sorted(by_type(rows, "jpeg"), key=lambda r: r["dataset_size_mb"])
        bpc_rows = sorted(bpc_quantized_rows(rows), key=lambda r: r["dataset_size_mb"])
        
        ax.plot([r["dataset_size_mb"] for r in jpeg_rows], [r["map50"] for r in jpeg_rows], linestyle=style["linestyle"], marker=style["marker"], color=style["jpeg"], markeredgecolor='white', markeredgewidth=0.5, markersize=8)
        ax.plot([r["dataset_size_mb"] for r in bpc_rows], [r["map50"] for r in bpc_rows], linestyle=style["linestyle"], marker=style["marker"], color=style["bpc"], markeredgecolor='white', markeredgewidth=0.5, markersize=8)
        
    ax.set_title("All Models Comparison", pad=15)
    ax.set_xlabel("Dataset size (MB)", labelpad=10)
    ax.set_ylabel("mAP50", labelpad=10)
    
    ax.set_axisbelow(True)
    ax.minorticks_on()
    ax.grid(True, which='major', linestyle='-', linewidth=0.75, alpha=0.3)
    ax.grid(True, which='minor', linestyle='-', linewidth=0.25, alpha=0.15)
    
    custom_lines = [
        Line2D([0], [0], color=MODEL_STYLES["YOLOv8n"]["jpeg"], linestyle=MODEL_STYLES["YOLOv8n"]["linestyle"], marker='D', markersize=8, markeredgecolor='white', markeredgewidth=0.5, label='YOLOv8n JPEG'),
        Line2D([0], [0], color=MODEL_STYLES["YOLOv8n"]["bpc"], linestyle=MODEL_STYLES["YOLOv8n"]["linestyle"], marker='D', markersize=8, markeredgecolor='white', markeredgewidth=0.5, label='YOLOv8n BPC'),
        Line2D([0], [0], color=MODEL_STYLES["YOLOv8m"]["jpeg"], linestyle=MODEL_STYLES["YOLOv8m"]["linestyle"], marker='s', markersize=8, markeredgecolor='white', markeredgewidth=0.5, label='YOLOv8m JPEG'),
        Line2D([0], [0], color=MODEL_STYLES["YOLOv8m"]["bpc"], linestyle=MODEL_STYLES["YOLOv8m"]["linestyle"], marker='s', markersize=8, markeredgecolor='white', markeredgewidth=0.5, label='YOLOv8m BPC'),
        Line2D([0], [0], color=MODEL_STYLES["RT-DETR-L"]["jpeg"], linestyle=MODEL_STYLES["RT-DETR-L"]["linestyle"], marker='o', markersize=8, markeredgecolor='white', markeredgewidth=0.5, label='RT-DETR-L JPEG'),
        Line2D([0], [0], color=MODEL_STYLES["RT-DETR-L"]["bpc"], linestyle=MODEL_STYLES["RT-DETR-L"]["linestyle"], marker='o', markersize=8, markeredgecolor='white', markeredgewidth=0.5, label='RT-DETR-L BPC')
    ]
    ax.legend(handles=custom_lines, fontsize=10, loc="lower right", frameon=False)

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
                axes[i].legend(fontsize=11, loc="lower right", frameon=False)
        else:
            print(f"File not found: {path}")
            
    plot_all_models_ax(axes[3], all_data)
    
    plt.tight_layout()
    out_path = out_dir / "fig_multi_model_grid.png"
    plt.savefig(out_path, dpi=300)
    print(f"Saved {out_path}")

if __name__ == "__main__":
    main()
