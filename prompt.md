You are an experienced PhD researcher and academic writer specializing in computer vision, image compression, and experimental evaluation of deep learning systems.

Your task is to write a full scientific article in English based on the local research project located at:

`/Users/amirkarataev/Desktop/dissertation/dtiq/`

The article must be suitable for submission to a journal with formatting similar to the Scientific Journal of Astana IT University.

# Main Article Topic

Write a scientific article on the following topic:

**Task-Aware Analysis of JPEG Recompression and Bit-Depth Reduction for Efficient Image Compression in Object Detection**

The article is based on the master's dissertation topic:

**Development and Analysis of Quantization Methods for Efficient Compression of Images**

The article must present this project as a first empirical study of the dissertation. Do not claim that a new compression algorithm was invented. The contribution is an experimental, task-aware comparison of image degradation/compression strategies for object detection.

# Required Source Files To Read First

Before writing, read and use the following files from the project:

## Main Project Description

- `README.md`

## Research Notes

- `article_notes/academic_reasons.md`
- `article_notes/info.md`

## Final Experiment Results

- `results/val5k/summary/metrics.csv`
- `results/val5k/summary/image_quality.csv`
- `results/val5k/summary/summary.md`
- `results/val5k/summary/full_report.md`
- `results/val5k/summary/final_table.md`

## Pilot Experiment Results

- `results/val500/summary/metrics.csv`
- `results/val500/summary/image_quality.csv`
- `results/val500/summary/summary.md`
- `results/val500/summary/full_report.md`

## Article Figures

Use the following figures as article-ready figures:

- `results/article_figures/fig1_map50_vs_size.svg`
- `results/article_figures/fig2_compression_ratio_vs_map50.svg`
- `results/article_figures/fig3_relative_map50_drop.svg`
- `results/article_figures/fig4_dataset_size_bars.svg`
- `results/article_figures/fig5_detection_metric_bars.svg`
- `results/article_figures/fig6_psnr_vs_map50.svg`
- `results/article_figures/fig7_ssim_vs_map50.svg`
- `results/article_figures/fig8_jpeg_visual_degradation_grid.svg` or `.png`
- `results/article_figures/fig9_bpc_visual_degradation_grid.svg` or `.png`

If the exact extension of `fig8` and `fig9` differs, refer to the figure name without inventing data.

# Core Experimental Setup

The final official experiment is:

- Dataset: `COCO val2017`
- Number of images: `5000`
- Model: `YOLOv8n`
- Device: `CPU`
- Image size: `640`
- Batch size: `1`
- Workers: `0`

Compared variants:

- `original`
- JPEG recompression: `q94`, `q88`, `q75`, `q50`, `q25`
- Bit-depth reduction stored as PNG: `b7`, `b4`, `b3`, `b2`, `b1`

Use the term **BPC** to mean bit-depth reduction in bits per channel.

Important methodological precision:

The article must state that the comparison is between:

- JPEG recompression
- uniform RGB bit-depth reduction stored as PNG

Do not generalize the conclusion to all possible bit-depth reduction methods or all possible codecs.

# Main Numerical Results To Use

Use exact values from `results/val5k/summary/metrics.csv` and `results/val5k/summary/image_quality.csv`.

Important final results:

| Variant | Type | Size MB | Compression Ratio | mAP50 | mAP50-95 | PSNR | SSIM |
|---|---:|---:|---:|---:|---:|---:|---:|
| original | original | 776.9634 | 1.00x | 0.5187 | 0.3681 | — | — |
| q94 | JPEG | 543.3825 | 1.43x | 0.5162 | 0.3660 | 37.4721 | 0.9677 |
| q88 | JPEG | 384.2208 | 2.02x | 0.5147 | 0.3647 | 35.3911 | 0.9477 |
| q75 | JPEG | 239.2142 | 3.25x | 0.5057 | 0.3563 | 32.2933 | 0.9055 |
| q50 | JPEG | 156.6916 | 4.96x | 0.4814 | 0.3360 | 30.1392 | 0.8662 |
| q25 | JPEG | 95.9412 | 8.10x | 0.4073 | 0.2742 | 28.1373 | 0.8142 |
| b7 | BPC | 1912.6668 | 0.41x | 0.5189 | 0.3680 | 51.2191 | 0.9980 |
| b4 | BPC | 816.7964 | 0.95x | 0.4987 | 0.3509 | 34.4830 | 0.9064 |
| b3 | BPC | 607.8120 | 1.28x | 0.4393 | 0.3040 | 27.8577 | 0.7862 |
| b2 | BPC | 322.7558 | 2.41x | 0.2912 | 0.1942 | 20.5138 | 0.6009 |
| b1 | BPC | 165.5969 | 4.69x | 0.1328 | 0.0827 | 10.9245 | 0.3089 |

Key interpretation:

- `q88` is the strongest near-baseline trade-off: around `2.02x` compression with less than `1%` relative mAP50 loss.
- `q75` is a strong practical compromise: around `3.25x` compression with moderate detection degradation.
- `q94` is near-baseline with smaller storage reduction.
- `q25` is not the best scientific trade-off; it is the most aggressive JPEG point and has substantial detection loss.
- `b7` has excellent PSNR/SSIM and preserves detection quality, but it is much larger than the original dataset.
- `b4` is the main BPC threshold point, but it does not reduce storage compared with the original.
- `b2` and `b1` strongly damage detection quality.
- High PSNR/SSIM alone is insufficient for judging compression usefulness in object detection.

# Required Article Structure

Write the article with the following structure:

# Title

Use this exact title unless a slightly more academic variant is clearly better:

**Task-Aware Analysis of JPEG Recompression and Bit-Depth Reduction for Efficient Image Compression in Object Detection**

# Abstract

Write 250–280 words.

The abstract must include:

- problem context;
- research gap;
- dataset and model;
- compared methods;
- metrics;
- key numerical results;
- main conclusion;
- limitation that the BPC branch is evaluated as `BPC + PNG`.

# Keywords

No more than 10 keywords.

Recommended keywords:

Image Compression, Quantization, JPEG Recompression, Bit-Depth Reduction, Object Detection, YOLOv8, COCO Dataset, PSNR, SSIM, mAP

# Introduction

Explain:

- why image compression matters for computer vision systems;
- why visual quality alone is insufficient;
- why task-aware evaluation is needed;
- why object detection is a meaningful downstream task;
- the research question;
- the contribution of the paper.

Do not exaggerate novelty. Present novelty as a controlled empirical comparison of two degradation mechanisms under object detection metrics.

# Literature Review

Discuss related work in these groups:

1. Classical image compression and JPEG.
2. Image quality metrics such as PSNR and SSIM.
3. Quantization and bit-depth reduction.
4. Object detection with YOLO-type models.
5. Task-aware compression evaluation for computer vision.

Use citation placeholders in numeric form such as `[1]`, `[2]`, `[3–5]`.

Do not invent exact bibliographic entries unless asked. If references are needed, add a section called `References` with placeholders and clear notes that they must be replaced with verified sources.

# Methods and Materials

Describe:

- Dataset: COCO val2017, 5000 images.
- Model: YOLOv8n.
- Input size: 640.
- Hardware/device: CPU for final official experiment.
- JPEG variants: q94, q88, q75, q50, q25.
- BPC variants: b7, b4, b3, b2, b1.
- Storage formats: JPEG variants saved as JPEG; BPC variants saved as PNG.
- Evaluation metrics: dataset size, compression ratio, PSNR, SSIM, Precision, Recall, mAP50, mAP50-95.
- Pilot experiment on 500 images and final experiment on 5000 images.

Include formulas for compression ratio and relative mAP drop:

$$
CR = \frac{S_{original}}{S_{variant}}
$$

$$
\Delta mAP50 = \frac{mAP50_{original} - mAP50_{variant}}{mAP50_{original}} \times 100\%
$$

# Results

Use the final `val5k` experiment as the main result.

Include a Markdown table with the final results.

Discuss the figures in this order:

- Fig. 1. mAP50 versus dataset size.
- Fig. 2. Compression ratio versus mAP50.
- Fig. 3. Relative mAP50 drop under compression.
- Fig. 4. Dataset size by variant.
- Fig. 5. Detection metrics by variant.
- Fig. 6. PSNR versus mAP50.
- Fig. 7. SSIM versus mAP50.
- Fig. 8. Visual degradation examples for JPEG recompression.
- Fig. 9. Visual degradation examples for bit-depth reduction.

Before every figure mention it in the text, for example:

`The relationship between dataset size and detection quality is shown in Fig. 1.`

Then include a caption line in the following form:

`Fig. 1. Detection quality as a function of dataset size for original, JPEG, and BPC variants.`

Do not embed binary images in the Markdown unless asked. Refer to file paths and captions.

# Discussion

Interpret:

- why JPEG q88 and q75 are strong practical points;
- why q25 should not be presented as the best trade-off despite its small size;
- why BPC has high PSNR/SSIM at b7 but poor storage efficiency;
- why PSNR/SSIM and mAP can diverge;
- why BPC + PNG is the correct scope of the conclusion;
- how the 500-image pilot supports the 5000-image final result.

Be scientifically cautious. Use phrases such as:

- “under the tested conditions”
- “in the evaluated BPC + PNG scheme”
- “near-baseline performance”
- “storage–accuracy trade-off”

Avoid phrases such as:

- “JPEG is always better”
- “BPC is useless”
- “lossless quality”
- “proved for all object detectors”

# Conclusion

Summarize:

- main finding;
- best practical JPEG regimes;
- scientific value of negative BPC result;
- limitations;
- future work.

Future work should include:

- additional codecs such as WebP, AVIF, JPEG XL;
- other YOLO models or detector families;
- learned compression methods;
- statistical repeated runs;
- more advanced entropy coding for reduced bit-depth images;
- per-class detection analysis.

# Formatting Rules

Output only Markdown with LaTeX math.

Use:

- `#`, `##`, `###` headings.
- Markdown tables.
- Inline math with `$...$`.
- Display math with `$$...$$`.
- Figure captions as plain text: `Fig. 1. Title.`
- Table captions as plain text: `Table 1. Title.`
- Numeric citations in the text: `[1]`, `[2]`, `[3–5]`.

Do not use:

- `\textbf{}` for normal bold text.
- LaTeX `tabular`.
- raw HTML.
- invented file paths.
- invented numerical results.
- overclaiming.

# Journal Formatting Constraints To Respect Conceptually

The final article will later be converted to `.tex` or `.docx`.

Keep in mind:

- English language.
- Minimum article length should be suitable for approximately 8 journal pages.
- Abstract should be 250–280 words.
- No more than 10 keywords.
- Figures must be referenced before placement.
- Figure captions must follow the form `Fig. N. Title.`
- Tables must be vertical and readable.
- References should ultimately contain at least 20 sources in APA style, but if verified sources are not provided, use citation placeholders and mark that references must be verified.

# Writing Style

Use a strict academic tone.

Avoid empty phrases and generic statements.

Write deeply and concretely.

Base every claim on the project data.

If a result is from the final `val5k` experiment, say so.

If a result is from the pilot `val500` experiment, say so.

Do not mix pilot and final results without clearly distinguishing them.

# Final Output

Produce a complete first draft of the article in Markdown.

The article should be coherent, publication-oriented, and ready for later manual editing, citation verification, and formatting according to the journal template.