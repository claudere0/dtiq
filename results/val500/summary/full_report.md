# Full Experiment Report

## 1. Goal of the Experiment

The goal of this experiment was to evaluate how different image quantization strategies affect the detection quality of `YOLOv8n` on a subset of `500` images from `COCO val2017`.

The study focused on the trade-off between:

- object detection quality;
- dataset storage size.

Three groups were compared:

- `original` — original images;
- `JPEG` — repeated JPEG compression with quality levels `94, 88, 75, 50, 25`;
- `BPC` — bit-depth reduction to `7, 4, 3, 2, 1` bits per channel with storage in `PNG`.

## 2. Configuration

Based on the metadata in [results/val500/metrics](/Users/amirkarataev/Desktop/dissertation/dtiq/results/val500/metrics):

- model: `yolov8n.pt`
- device: `mps`
- image size: `640`
- `batch=1`
- `workers=0`
- sample size: `500` images
- dataset: subset of `COCO val2017`

The main metrics were:

- `Precision`
- `Recall`
- `mAP50`
- `mAP50-95`

The total size of the image folders was also analyzed.

## 3. Final Results

Source table: [metrics.csv](/Users/amirkarataev/Desktop/dissertation/dtiq/results/val500/summary/metrics.csv:1)

| Variant | Type | Size (MB) | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| original | original | 77.1354 | 0.6828 | 0.4894 | 0.5591 | 0.4056 |
| q94 | jpeg | 53.9552 | 0.6737 | 0.4913 | 0.5543 | 0.4039 |
| q88 | jpeg | 38.0456 | 0.6923 | 0.4830 | 0.5547 | 0.4028 |
| q75 | jpeg | 23.7281 | 0.6478 | 0.4866 | 0.5424 | 0.3923 |
| q50 | jpeg | 15.5205 | 0.6366 | 0.4639 | 0.5199 | 0.3729 |
| q25 | jpeg | 9.4916 | 0.5757 | 0.4055 | 0.4419 | 0.3039 |
| b7 | bpc | 189.5861 | 0.6674 | 0.4972 | 0.5597 | 0.4056 |
| b4 | bpc | 80.7269 | 0.6709 | 0.4613 | 0.5358 | 0.3843 |
| b3 | bpc | 59.8888 | 0.6352 | 0.4078 | 0.4711 | 0.3316 |
| b2 | bpc | 31.7699 | 0.4566 | 0.3100 | 0.3139 | 0.2130 |
| b1 | bpc | 16.0452 | 0.3453 | 0.1671 | 0.1520 | 0.0996 |

## 4. Main Observations for JPEG

The JPEG branch looks very strong.

- `q94` is almost identical to baseline:
  - `mAP50`: `0.554` versus `0.559`
  - size drops from `77.1 MB` to `54.0 MB`
- `q88` is especially interesting:
  - `mAP50 = 0.555`
  - size `38.0 MB`
  - this is almost baseline-level quality at about half the size
- `q75` remains a strong compromise:
  - `mAP50 = 0.542`
  - size `23.7 MB`
- `q50` already shows visible degradation, but still remains usable
- `q25` is clearly aggressive:
  - `mAP50 = 0.442`
  - size `9.5 MB`
  - quality drops noticeably, but not to total collapse

Conclusion for JPEG:
`q88` and `q94` preserve detection quality almost at baseline level while reducing storage substantially. `q75` also looks like a strong practical compromise. `q50` and `q25` move deeper into the aggressive compression regime.

## 5. Main Observations for BPC

The BPC branch confirms that moderate bit-depth reduction can preserve task-relevant information, but its storage efficiency is much weaker.

- `b7`:
  - `mAP50 = 0.560`, essentially equal to `original`
  - but size is `189.6 MB`, much worse than baseline
- `b4`:
  - `mAP50 = 0.536`
  - size `80.7 MB`
  - quality is still reasonably close to baseline, but storage gain is almost absent
- `b3`:
  - already noticeable drop: `mAP50 = 0.471`
  - size `59.9 MB`
- `b2`:
  - strong degradation: `mAP50 = 0.314`
- `b1`:
  - near collapse: `mAP50 = 0.152`

Conclusion for BPC:
bit-depth reduction does not immediately destroy detection performance, but in the current `BPC + PNG` setup it does not provide a good quality-to-size trade-off. The upper part of the scale (`b7`, `b4`) preserves quality better but has poor storage behavior, while the lower part (`b2`, `b1`) reduces size at the cost of severe quality loss.

## 6. Direct Comparison of JPEG and BPC

This is the key part of the experiment.

### Near-baseline comparison

- `original`: `77.1 MB`, `mAP50 = 0.559`
- `q88`: `38.0 MB`, `mAP50 = 0.555`
- `q94`: `54.0 MB`, `mAP50 = 0.554`
- `b7`: `189.6 MB`, `mAP50 = 0.560`
- `b4`: `80.7 MB`, `mAP50 = 0.536`

Conclusion:

- `b7` is nearly equal to baseline in quality, but dramatically worse in size
- `q88` is nearly equal to baseline in quality and much better in size
- `q94` is also a strong near-baseline point

### Mid-range trade-off comparison

- `q75`: `23.7 MB`, `mAP50 = 0.542`
- `b3`: `59.9 MB`, `mAP50 = 0.471`
- `b4`: `80.7 MB`, `mAP50 = 0.536`

Conclusion:
JPEG clearly dominates here in both size and quality.

### Aggressive compression comparison

- `q25`: `9.5 MB`, `mAP50 = 0.442`
- `b2`: `31.8 MB`, `mAP50 = 0.314`
- `b1`: `16.0 MB`, `mAP50 = 0.152`

Conclusion:
even aggressive JPEG `q25` performs much better than `b2` and `b1`, while also being more storage efficient.

## 7. Main Scientific Conclusion

If formulated carefully:

On a subset of `500` images from `COCO val2017`, repeated JPEG compression was a more effective method for reducing data size while preserving `YOLOv8n` detection performance than bit-depth reduction with storage in `PNG`.

A more precise version is:
moderate bit-depth reduction can preserve task-relevant information, but in the current `BPC + PNG` storage scheme it is less effective than `JPEG recompression` in terms of the relationship between dataset size and detection quality.

## 8. What Is Especially Interesting for the Paper

The strongest points are:

- `q88` — almost baseline quality at about half the size
- `q94` — a mild near-baseline regime
- `q75` — a very strong practical compromise
- `b4` — an interesting threshold point inside the BPC branch
- `b7` — an important negative result: almost baseline quality, but much worse size

This makes the paper stronger, because the experiment does not only show a winning method, but also explains why the alternative method loses specifically as a size-versus-detection trade-off.

## 9. Careful Interpretation

Some claims should still be phrased cautiously:

- `b7` being slightly above `original` in `mAP50` does not mean BPC is better than the original; this should be interpreted as practically equivalent
- the differences between `q88`, `q94`, and `original` are very small, so it is better to say "near-baseline performance" rather than "lossless"
- the result currently applies to:
  - one model (`YOLOv8n`)
  - one sample (`500`)
  - one BPC storage implementation (`PNG`)
  - one validation setup

## 10. Limitations

These limitations should be stated explicitly:

- only one model was used: `YOLOv8n`
- only one sample size was used: `500` images
- only one BPC storage format was tested: `PNG`
- the JPEG branch uses recompression of already-JPEG images
- PSNR and SSIM are not yet included
- repeated runs or statistical stability checks were not yet performed

## 11. Practical Conclusion

From both a research and engineering perspective:

- if the goal is to preserve detection quality while reducing size, the strongest region is currently `q88` and `q75`
- if the focus is specifically on BPC behavior, the most informative point is `b4`
- `b2` and `b1` are useful as examples of signal destruction, but not as practical operating points

## 12. Final Summary

Yes, this experiment was successful and informative. It shows not random noise, but a clear structural pattern:

- JPEG degrades gradually and efficiently
- BPC also produces a predictable degradation scale
- but in the `BPC + PNG` form it loses to JPEG in the `size vs mAP` trade-off

This is already strong material for the results section of a scientific paper.
