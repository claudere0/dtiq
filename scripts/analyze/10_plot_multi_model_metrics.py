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
    "YOLOv8n": {"marker": "D", "jpeg": "#9671bd", "bpc": "#6a408d"},
    "YOLOv8m": {"marker": "s", "jpeg": "#77b5b6", "bpc": "#378d94"},
    "RT-DETR-L": {"marker": "o", "jpeg": "#f2ad73", "bpc": "#c45a16"}
}

MODELS = [
    ("YOLOv8n", "results/val5k_yolov8n/summary/metrics.csv"),
    ("YOLOv8m", "results/val5k_yolov8m/summary/metrics.csv"),
    ("RT-DETR-L", "results/val5k_rtdetr_l/summary/metrics.csv"),
]

IMAGE_QUALITY_CSV = "results/val5k/summary/image_quality.csv"

def load_quality_rows(path):
    with Path(path).open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    
    quality_map = {}
    for row in rows:
        variant = row["variant"]
        if row.get("mean_psnr"):
            psnr = float(row["mean_psnr"])
            ssim = float(row["mean_ssim"])
            quality_map[variant] = {"psnr": psnr, "ssim": ssim}
    return quality_map

def load_metrics_rows(path, quality_map):
    with Path(path).open("r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    
    processed = []
    for row in rows:
        variant = row["variant"]
        if variant == "original" or variant == "b8":
            continue
        
        q_type = row["quantization_type"]
        size_mb = float(row["dataset_size_mb"])
        map50 = float(row["map50"])
        
        psnr = quality_map.get(variant, {}).get("psnr", None)
        ssim = quality_map.get(variant, {}).get("ssim", None)
        
        processed.append({
            "variant": variant,
            "type": q_type,
            "size_mb": size_mb,
            "map50": map50,
            "psnr": psnr,
            "ssim": ssim,
        })
    return processed

def get_pareto_frontier(rows):
    candidates = sorted(rows, key=lambda row: (row["size_mb"], -row["map50"]))
    frontier = []
    best_map = -1.0
    for row in candidates:
        if row["map50"] > best_map:
            frontier.append(row)
            best_map = row["map50"]
    return sorted(frontier, key=lambda row: row["size_mb"])

def plot_scatter_multi(ax, all_data, x_key, title, xlabel, ylabel):
    for model_name, rows in all_data:
        style = MODEL_STYLES[model_name]
        jpeg_rows = [r for r in rows if r["type"] == "jpeg" and r[x_key] is not None]
        bpc_rows = [r for r in rows if r["type"] == "bpc" and r[x_key] is not None]
        
        if jpeg_rows:
            ax.scatter([r[x_key] for r in jpeg_rows], [r["map50"] for r in jpeg_rows], marker=style["marker"], color=style["jpeg"], edgecolors='white', linewidths=0.5, s=110, zorder=3)
        if bpc_rows:
            ax.scatter([r[x_key] for r in bpc_rows], [r["map50"] for r in bpc_rows], marker=style["marker"], color=style["bpc"], edgecolors='white', linewidths=0.5, s=110, zorder=3)
            
    ax.set_title(title, pad=15)
    ax.set_xlabel(xlabel, labelpad=10)
    ax.set_ylabel(ylabel, labelpad=10)
    
    ax.set_axisbelow(True)
    ax.minorticks_on()
    ax.grid(True, which='major', linestyle='-', linewidth=0.75, alpha=0.3)
    ax.grid(True, which='minor', linestyle='-', linewidth=0.25, alpha=0.15)
    
    custom_lines = [
        Line2D([0], [0], color='w', marker='D', markerfacecolor='#6a408d', markeredgecolor='white', markersize=9, label='YOLOv8n'),
        Line2D([0], [0], color='w', marker='s', markerfacecolor='#378d94', markeredgecolor='white', markersize=9, label='YOLOv8m'),
        Line2D([0], [0], color='w', marker='o', markerfacecolor='#c45a16', markeredgecolor='white', markersize=9, label='RT-DETR-L'),
        Line2D([0], [0], color='#aaaaaa', linewidth=3, label='JPEG (Light)'),
        Line2D([0], [0], color='#444444', linewidth=3, label='BPC (Dark)')
    ]
    ax.legend(handles=custom_lines, fontsize=11, loc='lower right', frameon=False)

def plot_pareto_multi(ax, all_data):
    for model_name, rows in all_data:
        style = MODEL_STYLES[model_name]
        jpeg_rows = [r for r in rows if r["type"] == "jpeg"]
        bpc_rows = [r for r in rows if r["type"] == "bpc"]
        
        if jpeg_rows:
            ax.scatter([r["size_mb"] for r in jpeg_rows], [r["map50"] for r in jpeg_rows], marker=style["marker"], color=style["jpeg"], edgecolors='white', linewidths=0.5, s=110, zorder=3)
        if bpc_rows:
            ax.scatter([r["size_mb"] for r in bpc_rows], [r["map50"] for r in bpc_rows], marker=style["marker"], color=style["bpc"], edgecolors='white', linewidths=0.5, s=110, zorder=3)
            
        frontier = get_pareto_frontier(rows)
        if frontier:
            ax.plot([r["size_mb"] for r in frontier], [r["map50"] for r in frontier], linestyle='--', color="#888888", linewidth=2.5, alpha=0.6, zorder=2)
            
    ax.set_title("Storage-detection Pareto frontier", pad=15)
    ax.set_xlabel("Dataset size (MB)", labelpad=10)
    ax.set_ylabel("mAP50", labelpad=10)
    
    ax.set_axisbelow(True)
    ax.minorticks_on()
    ax.grid(True, which='major', linestyle='-', linewidth=0.75, alpha=0.3)
    ax.grid(True, which='minor', linestyle='-', linewidth=0.25, alpha=0.15)
    
    custom_lines = [
        Line2D([0], [0], color='w', marker='D', markerfacecolor='#6a408d', markeredgecolor='white', markersize=9, label='YOLOv8n'),
        Line2D([0], [0], color='w', marker='s', markerfacecolor='#378d94', markeredgecolor='white', markersize=9, label='YOLOv8m'),
        Line2D([0], [0], color='w', marker='o', markerfacecolor='#c45a16', markeredgecolor='white', markersize=9, label='RT-DETR-L'),
        Line2D([0], [0], color='#aaaaaa', linewidth=3, label='JPEG (Light)'),
        Line2D([0], [0], color='#444444', linewidth=3, label='BPC (Dark)'),
        Line2D([0], [0], linestyle='--', color="#888888", linewidth=2.5, alpha=0.6, label='Pareto Frontier')
    ]
    ax.legend(handles=custom_lines, fontsize=11, loc='lower right', frameon=False)

def main():
    out_dir = Path("article/latex_project/results/article_figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    quality_map = load_quality_rows(IMAGE_QUALITY_CSV)
    
    all_data = []
    for name, path in MODELS:
        if Path(path).exists():
            rows = load_metrics_rows(path, quality_map)
            all_data.append((name, rows))
            
    # PSNR
    fig, ax = plt.subplots(figsize=(10, 8))
    plot_scatter_multi(ax, all_data, "psnr", "PSNR vs detection quality", "Mean PSNR", "mAP50")
    plt.tight_layout()
    plt.savefig(out_dir / "fig6_psnr_vs_map50.png", dpi=300)
    plt.close(fig)
    
    # SSIM
    fig, ax = plt.subplots(figsize=(10, 8))
    plot_scatter_multi(ax, all_data, "ssim", "SSIM vs detection quality", "Mean SSIM", "mAP50")
    plt.tight_layout()
    plt.savefig(out_dir / "fig7_ssim_vs_map50.png", dpi=300)
    plt.close(fig)
    
    # Pareto
    fig, ax = plt.subplots(figsize=(10, 8))
    plot_pareto_multi(ax, all_data)
    plt.tight_layout()
    plt.savefig(out_dir / "fig10_pareto_storage_map50.png", dpi=300)
    plt.close(fig)

if __name__ == "__main__":
    main()
