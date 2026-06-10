# Task-Aware Analysis of JPEG Recompression and Bit-Depth Reduction for Efficient Image Compression in Object Detection

This repository contains an experimental pipeline for studying how image compression and quantization affect downstream object detection quality.

The project compares two image degradation strategies on `COCO val2017` using `YOLOv8n`:

- `JPEG recompression` with quality levels `94, 88, 75, 50, 25`;
- `bit-depth reduction` to `7, 4, 3, 2, 1` bits per channel, stored as `PNG`.

The main research question is not only how much the image files can be compressed, but how much task-relevant information remains for object detection.

## Research Focus

The project evaluates the trade-off between:

- dataset storage size;
- classical image quality metrics: `PSNR` and `SSIM`;
- object detection metrics: `Precision`, `Recall`, `mAP50`, and `mAP50-95`.

The final `val5k` experiment shows that moderate JPEG recompression provides a stronger storage-versus-detection trade-off than the tested `BPC + 24-bit PNG` scheme.

## Project Structure

```text
configs/
  experiment_5k.yaml         # final 5000-image validation setup
  datasets/                  # YOLO dataset configs for all variants

data/
  source/coco/                  # COCO val2017 images and YOLO labels
  processed/                 # generated variants, ignored by git

scripts/
  prepare/                   # dataset conversion and variant generation
  validate/                  # YOLOv8 validation runners
  analyze/                   # metric collection, image quality, plotting, summaries

results/
  val5k/                     # final experiment results
```

## Pipeline

### 1. Download COCO val2017 Dataset

Before running the pipeline, you must download the COCO val2017 images and annotations. You can download them manually from the [official COCO website](https://cocodataset.org/#download) or use the direct links below.

**Option A: Manual Download (Browser)**
1. Download [val2017.zip](http://images.cocodataset.org/zips/val2017.zip) and extract it inside `data/source/coco/images/`. The final image folder should be `data/source/coco/images/val2017/`.
2. Download [annotations_trainval2017.zip](http://images.cocodataset.org/annotations/annotations_trainval2017.zip) and extract it so that the JSON files are inside `data/source/coco/annotations/`. (Specifically, you need `instances_val2017.json`).

**Option B: Terminal (curl/wget)**
```bash
mkdir -p data/source/coco/images
mkdir -p data/source/coco/annotations

# Download and extract images
curl -O http://images.cocodataset.org/zips/val2017.zip
unzip val2017.zip -d data/source/coco/images/
rm val2017.zip

# Download and extract annotations
curl -O http://images.cocodataset.org/annotations/annotations_trainval2017.zip
unzip annotations_trainval2017.zip -d data/source/coco/
rm annotations_trainval2017.zip
```

### 2. Convert COCO annotations to YOLO format

```bash
python scripts/prepare/coco_json_to_yolo.py
```

This creates YOLO-format labels from the COCO annotation JSON.

### 3. Generate the full `val5k` experiment variants

```bash
python scripts/prepare/create_val5k_all_variants.py
```

This creates:

- original `COCO val2017` copy;
- JPEG variants: `q94`, `q88`, `q75`, `q50`, `q25`;
- BPC variants: `b8` (decoded JPEG → PNG control), `b7`, `b4`, `b3`, `b2`, `b1`.

### 4. Run YOLO validation

Final experiment:

```bash
python scripts/validate/run_all_validations.py --experiment-config configs/experiment_5k.yaml --exist-ok
```

The final official `val5k` results use:

- model: `YOLOv8n`;
- dataset: `COCO val2017`, `5000` images;
- device: `cpu`;
- image size: `640`;
- batch: `1`;
- workers: `0`.

Reproducibility note:

- hardware: Apple M1 MacBook Air with `8 GB` unified memory;
- operating system: `macOS 15.6.1`;
- core libraries: `ultralytics 8.4.52`, `torch 2.6.0`, `torchvision 0.21.0`, `numpy 2.2.6`, `pillow 10.4.0`, `opencv-python 4.12.0.88`, `scipy 1.15.1`, `scikit-image 0.26.0`, `PyYAML 6.0.2`, `pycocotools 2.0.11`.

### 5. Collect detection metrics

```bash
python scripts/analyze/collect_metrics.py --experiment-config configs/experiment_5k.yaml
python scripts/analyze/summarize_results.py --metrics-csv results/val5k/summary/metrics.csv
```

### 6. Compute image quality metrics

```bash
python scripts/analyze/compute_image_quality.py --experiment-config configs/experiment_5k.yaml --jobs 4
python scripts/analyze/summarize_image_quality.py --image-quality-csv results/val5k/summary/image_quality.csv
```

This computes per-image and aggregate `PSNR` and `SSIM` values for every non-original variant.

### 7. Generate plots

```bash
python scripts/analyze/plot_results.py \
  --metrics-csv results/val5k/summary/metrics.csv \
  --image-quality-csv results/val5k/summary/image_quality.csv
```

Generated plots:

- `results/val5k/plots/map50_vs_size.png`;
- `results/val5k/plots/map50_95_vs_size.png`;

### 8. Generate article-ready figures

```bash
python scripts/analyze/make_article_figures.py \
  --metrics-csv results/val5k/summary/metrics.csv \
  --image-quality-csv results/val5k/summary/image_quality.csv \
  --output-dir article/latex_project/results/article_figures
```

This creates a dedicated article figure folder with SVG files, the main merged table, and the supplementary LZMA summary:

- `article/latex_project/results/article_figures/article_metrics_table.csv`;
- `article/latex_project/results/article_figures/lzma_storage.csv`;
- `article/latex_project/results/article_figures/fig1`–`fig7` (`.svg` and `.png`);
- `article/latex_project/results/article_figures/fig10_pareto_storage_map50` (`.svg` and `.png`);
- `article/latex_project/results/article_figures/fig8_jpeg_visual_degradation_grid.png`;
- `article/latex_project/results/article_figures/fig9_bpc_visual_degradation_grid.png`.

If you regenerate the auxiliary `BMP + LZMA` experiment separately, you can refresh just that supplementary table with:

```bash
python scripts/analyze/summarize_lzma_storage.py \
  --article-metrics-csv article/latex_project/results/article_figures/article_metrics_table.csv \
  --lzma-root data/processed/val5k/bpc_lzma
```

Recommended additional visual examples for the paper:

- `original`;
- `q88`;
- `q75`;
- `q25`;
- `b4`;
- `b2`;
- `b1`.

## Final `val5k` Results

| Variant | Type | Size (MB) | Compression Ratio | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| original | original | 776.9634 | 1.00x | 0.6347 | 0.4739 | 0.5187 | 0.3681 |
| q94 | jpeg | 543.3825 | 1.43x | 0.6357 | 0.4691 | 0.5162 | 0.3660 |
| q88 | jpeg | 384.2208 | 2.02x | 0.6446 | 0.4641 | 0.5147 | 0.3647 |
| q75 | jpeg | 239.2142 | 3.25x | 0.6234 | 0.4660 | 0.5057 | 0.3563 |
| q50 | jpeg | 156.6916 | 4.96x | 0.6003 | 0.4456 | 0.4814 | 0.3360 |
| q25 | jpeg | 95.9412 | 8.10x | 0.5682 | 0.3783 | 0.4073 | 0.2742 |
| b8 | bpc (PNG control) | 2288.6569 | 0.34x | 0.6347 | 0.4739 | 0.5187 | 0.3681 |
| b7 | bpc | 1912.6668 | 0.41x | 0.6328 | 0.4761 | 0.5189 | 0.3680 |
| b4 | bpc | 816.7964 | 0.95x | 0.6081 | 0.4596 | 0.4987 | 0.3509 |
| b3 | bpc | 607.8120 | 1.28x | 0.5808 | 0.4097 | 0.4393 | 0.3040 |
| b2 | bpc | 322.7558 | 2.41x | 0.4904 | 0.2884 | 0.2912 | 0.1942 |
| b1 | bpc | 165.5969 | 4.69x | 0.3859 | 0.1501 | 0.1328 | 0.0827 |

## Final Image Quality Results

| Variant | Type | PSNR | SSIM |
|---|---:|---:|---:|
| q94 | jpeg | 37.4721 | 0.9677 |
| q88 | jpeg | 35.3911 | 0.9477 |
| q75 | jpeg | 32.2933 | 0.9055 |
| q50 | jpeg | 30.1392 | 0.8662 |
| q25 | jpeg | 28.1373 | 0.8142 |
| b7 | bpc | 51.2191 | 0.9980 |
| b4 | bpc | 34.4830 | 0.9064 |
| b3 | bpc | 27.8577 | 0.7862 |
| b2 | bpc | 20.5138 | 0.6009 |
| b1 | bpc | 10.9245 | 0.3089 |

## Main Findings

- `q94` and `q88` preserve near-baseline detection quality while substantially reducing storage size.
- `q88` is one of the strongest practical operating points: about `2.02x` compression with less than `1%` relative `mAP50` loss.
- `q75` remains a strong practical compromise: about `3.25x` compression with only moderate detection degradation.
- `q25` gives the smallest JPEG size, but its detection loss is too large to treat it as the best scientific trade-off.
- `b8` isolates the PNG container penalty: baseline-level detection with ~2.95× larger storage than the source JPEG baseline.
- `b7` preserves detection quality and has excellent `PSNR/SSIM`, but it is much larger than the original dataset.
- `b4` is the main threshold point for BPC: detection remains relatively close to baseline, but storage savings are absent.
- Aggressive BPC modes (`b2`, `b1`) strongly damage detection quality.

## Scientific Conclusion

On `COCO val2017` with `YOLOv8n`, JPEG recompression provides a more effective storage-versus-detection trade-off than uniform bit-depth reduction stored as 24-bit PNG.

The result should be interpreted carefully: the experiment does not prove that all bit-depth reduction methods are inferior to JPEG. It shows that, under the tested `BPC + 24-bit PNG` implementation, JPEG recompression is more efficient for preserving object detection performance at reduced dataset size. The container is part of the tested method: indexed PNG, bit-packing, or custom entropy coding may produce different storage behavior.

## Limitations

- Only one detector was evaluated: `YOLOv8n`.
- Only one dataset was used: `COCO val2017`.
- JPEG was applied as recompression to images already stored as JPEG.
- BPC variants were stored as 24-bit truecolor PNG, so the result concerns the complete `BPC + 24-bit PNG` storage scheme rather than all possible BPC containers.
- The current article-level comparison should be extended with additional codecs, models, and statistical stability checks.
