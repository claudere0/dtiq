import matplotlib.pyplot as plt
import numpy as np

# Set global academic style
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 12,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "legend.fontsize": 11,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "lines.linewidth": 2,
    "lines.markersize": 7
})

models = ['YOLOv8n', 'YOLOv8m', 'RT-DETR-L']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
markers = ['o', 's', '^']

# Data
jpeg_labels = ['Orig', 'q94', 'q88', 'q75', 'q50', 'q25']
jpeg_x = np.arange(len(jpeg_labels))
jpeg_maps = {
    'YOLOv8n': [0.0312, 0.0322, 0.0300, 0.0307, 0.0245, 0.0199],
    'YOLOv8m': [0.0523, 0.0505, 0.0490, 0.0466, 0.0383, 0.0283],
    'RT-DETR-L': [0.0542, 0.0521, 0.0521, 0.0498, 0.0445, 0.0414]
}

bpc_labels = ['b8', 'b7', 'b4', 'b3', 'b2', 'b1']
bpc_x = np.arange(len(bpc_labels))
bpc_maps = {
    'YOLOv8n': [0.0312, 0.0312, 0.0292, 0.0258, 0.0153, 0.0083],
    'YOLOv8m': [0.0523, 0.0524, 0.0500, 0.0446, 0.0292, 0.0151],
    'RT-DETR-L': [0.0542, 0.0541, 0.0524, 0.0502, 0.0389, 0.0225]
}

# Create a 1x2 subplot
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)

# Plot JPEG
for i, model in enumerate(models):
    axes[0].plot(jpeg_x, jpeg_maps[model], marker=markers[i], color=colors[i], label=model, linestyle='-')
axes[0].set_xticks(jpeg_x)
axes[0].set_xticklabels(jpeg_labels)
axes[0].set_xlabel('JPEG Quality Level')
axes[0].set_ylabel('mAP for Small Objects ($mAP_S$)')
axes[0].set_title('(a) JPEG Recompression')
axes[0].grid(True, linestyle='--', alpha=0.7)

# Plot BPC
for i, model in enumerate(models):
    axes[1].plot(bpc_x, bpc_maps[model], marker=markers[i], color=colors[i], label=model, linestyle='-')
axes[1].set_xticks(bpc_x)
axes[1].set_xticklabels(bpc_labels)
axes[1].set_xlabel('Uniform Bit-Depth Reduction (BPC)')
axes[1].set_title('(b) Bit-Depth Reduction')
axes[1].grid(True, linestyle='--', alpha=0.7)
axes[1].legend(loc='lower left')

plt.tight_layout()
output_path = "maps_degradation.pdf"
plt.savefig(output_path, format='pdf', bbox_inches='tight')
print(f"Successfully generated {output_path}")
