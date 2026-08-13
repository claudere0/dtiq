import matplotlib.pyplot as plt
import numpy as np
import os

# Set global styles
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

# Data
jpeg_labels = ['Orig', 'q94', 'q88', 'q75', 'q50', 'q25']
jpeg_data = {
    "YOLOv8n": [0.0312, 0.0322, 0.0300, 0.0307, 0.0245, 0.0199],
    "YOLOv8m": [0.0523, 0.0505, 0.0490, 0.0466, 0.0383, 0.0283],
    "RT-DETR-L": [0.0542, 0.0521, 0.0521, 0.0498, 0.0445, 0.0414]
}

bpc_labels = ['b8', 'b7', 'b4', 'b3', 'b2', 'b1']
bpc_data = {
    "YOLOv8n": [0.0312, 0.0312, 0.0292, 0.0258, 0.0153, 0.0083],
    "YOLOv8m": [0.0523, 0.0524, 0.0500, 0.0446, 0.0292, 0.0151],
    "RT-DETR-L": [0.0542, 0.0541, 0.0524, 0.0502, 0.0389, 0.0225]
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

# Subplot 1: JPEG Recompression
for model in ["YOLOv8n", "YOLOv8m", "RT-DETR-L"]:
    ax1.plot(jpeg_labels, jpeg_data[model], 
             marker=MODEL_STYLES[model]["marker"], 
             linestyle=MODEL_STYLES[model]["linestyle"], 
             color=MODEL_STYLES[model]["jpeg"], 
             linewidth=2.5, markersize=8, 
             markeredgecolor='white', markeredgewidth=1.0,
             label=model)

ax1.set_title('(a) JPEG Recompression')
ax1.set_xlabel('JPEG Quality Level')
ax1.set_ylabel('mAP for Small Objects (mAP_S)')
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend(frameon=False)

# Subplot 2: Bit-Depth Reduction
for model in ["YOLOv8n", "YOLOv8m", "RT-DETR-L"]:
    ax2.plot(bpc_labels, bpc_data[model], 
             marker=MODEL_STYLES[model]["marker"], 
             linestyle=MODEL_STYLES[model]["linestyle"], 
             color=MODEL_STYLES[model]["bpc"], 
             linewidth=2.5, markersize=8,
             markeredgecolor='white', markeredgewidth=1.0,
             label=model)

ax2.set_title('(b) Bit-Depth Reduction')
ax2.set_xlabel('Uniform Bit-Depth Reduction (BPC)')
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend(frameon=False)

plt.tight_layout()

output_path = "article/latex_project/results/article_figures/maps_degradation.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Saved {output_path}")
