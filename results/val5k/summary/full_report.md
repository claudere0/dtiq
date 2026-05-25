# Full Experiment Report

## 1. Goal of the Experiment

The goal of this experiment was to evaluate how different image quantization strategies affect the detection quality of `YOLOv8n` on the full `COCO val2017` validation set containing `5000` images.

The study focused on the trade-off between:

- object detection quality;
- dataset storage size.

Three groups were compared:

- `original` — original images;
- `JPEG` — repeated JPEG recompression with quality levels `94, 88, 75, 50, 25`;
- `BPC` — bit-depth reduction to `7, 4, 3, 2, 1` bits per channel with storage in `PNG`.

## 2. Final Experimental Configuration

The final official `val5k` experiment was executed with the following fixed setup:

- dataset: `COCO val2017` (`5000` images)
- model: `yolov8n.pt`
- device: `cpu`
- image size: `640`
- `batch=1`
- `workers=0`

Important clarification:

- `original_long_mps_check` and `original_slow_one` in `results/val5k` were exploratory and unsuccessful diagnostic attempts on `device=mps`
- they are **not** part of the final experiment
- the official results are the stable CPU-based runs stored in [metrics.csv](/Users/amirkarataev/Desktop/dissertation/dtiq/results/val5k/summary/metrics.csv:1)

The main metrics were:

- `Precision`
- `Recall`
- `mAP50`
- `mAP50-95`

The total storage size of each image set was also measured.

## 3. Final Results

| Variant | Type | Size (MB) | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| original | original | 776.9634 | 0.6347 | 0.4739 | 0.5187 | 0.3681 |
| q94 | jpeg | 543.3825 | 0.6357 | 0.4691 | 0.5162 | 0.3660 |
| q88 | jpeg | 384.2208 | 0.6446 | 0.4641 | 0.5147 | 0.3647 |
| q75 | jpeg | 239.2142 | 0.6234 | 0.4660 | 0.5057 | 0.3563 |
| q50 | jpeg | 156.6916 | 0.6003 | 0.4456 | 0.4814 | 0.3360 |
| q25 | jpeg | 95.9412 | 0.5682 | 0.3783 | 0.4073 | 0.2742 |
| b7 | bpc | 1912.6668 | 0.6328 | 0.4761 | 0.5189 | 0.3680 |
| b4 | bpc | 816.7964 | 0.6081 | 0.4596 | 0.4987 | 0.3509 |
| b3 | bpc | 607.8120 | 0.5808 | 0.4097 | 0.4393 | 0.3040 |
| b2 | bpc | 322.7558 | 0.4904 | 0.2884 | 0.2912 | 0.1942 |
| b1 | bpc | 165.5969 | 0.3859 | 0.1501 | 0.1328 | 0.0827 |

## 4. Main Observations for JPEG

The JPEG branch again shows a strong trade-off between compression and detection quality.

- `q94` is almost identical to baseline:
  - `mAP50 = 0.5162` versus `0.5187`
  - size decreases from `776.96 MB` to `543.38 MB`
- `q88` remains one of the most important operating points:
  - `mAP50 = 0.5147`
  - size `384.22 MB`
  - this preserves near-baseline performance at roughly half the original storage size
- `q75` remains a strong practical compromise:
  - `mAP50 = 0.5057`
  - size `239.21 MB`
- `q50` shows a clearer degradation:
  - `mAP50 = 0.4814`
  - size `156.69 MB`
- `q25` is strongly compressed:
  - `mAP50 = 0.4073`
  - size `95.94 MB`

Conclusion for JPEG:
`q94` and `q88` preserve object detection performance very close to the baseline while reducing storage substantially. `q75` also remains a strong practical operating point.

## 5. Main Observations for BPC

The BPC branch again shows that moderate bit-depth reduction can preserve task-relevant information, but the storage behavior of `BPC + PNG` is weak.

- `b7`:
  - `mAP50 = 0.5189`, essentially identical to the baseline
  - but size is `1912.67 MB`, far worse than the original
- `b4`:
  - `mAP50 = 0.4987`
  - size `816.80 MB`
  - quality is still relatively close to baseline, but storage gain is absent
- `b3`:
  - `mAP50 = 0.4393`
  - size `607.81 MB`
- `b2`:
  - `mAP50 = 0.2912`
  - strong degradation
- `b1`:
  - `mAP50 = 0.1328`
  - near collapse

Conclusion for BPC:
bit-depth reduction does not immediately destroy detection performance, but in the current tested storage scheme it does not deliver a competitive quality-to-size trade-off.

## 6. Direct Comparison of JPEG and BPC

This is the key result of the experiment.

### Near-baseline zone

- `original`: `776.96 MB`, `mAP50 = 0.5187`
- `q94`: `543.38 MB`, `mAP50 = 0.5162`
- `q88`: `384.22 MB`, `mAP50 = 0.5147`
- `b7`: `1912.67 MB`, `mAP50 = 0.5189`
- `b4`: `816.80 MB`, `mAP50 = 0.4987`

Conclusion:

- `b7` preserves baseline-level accuracy but is dramatically worse in storage size
- `q94` and `q88` preserve nearly the same detection quality while reducing storage substantially
- `q88` is especially strong because it roughly halves storage with only a very small loss in `mAP50`

### Mid-range compromise zone

- `q75`: `239.21 MB`, `mAP50 = 0.5057`
- `b4`: `816.80 MB`, `mAP50 = 0.4987`
- `b3`: `607.81 MB`, `mAP50 = 0.4393`

Conclusion:
JPEG clearly dominates BPC in both storage efficiency and detection quality.

### Aggressive compression zone

- `q25`: `95.94 MB`, `mAP50 = 0.4073`
- `b2`: `322.76 MB`, `mAP50 = 0.2912`
- `b1`: `165.60 MB`, `mAP50 = 0.1328`

Conclusion:
even aggressive JPEG compression remains substantially stronger than the corresponding aggressive BPC modes in terms of `size vs detection quality`.

## 7. Comparison with the Previous `val500` Experiment

The `val5k` experiment confirms the same structural pattern that was already visible on `val500`.

What remained consistent:

- JPEG remains better than `BPC + PNG` in the meaningful `size vs mAP` trade-off region
- `q94`, `q88`, and `q75` remain the strongest JPEG operating points
- `b7` remains near-baseline in detection quality but poor in storage size
- `b4` remains the main threshold point in the BPC branch
- `b2` and `b1` still show severe degradation

What improved scientifically:

- the full `5000`-image experiment greatly strengthens confidence in the conclusions
- the result is no longer only a pilot observation, but a stable full-scale empirical trend

## 8. Main Scientific Conclusion

The full-scale `val5k` experiment supports the following conclusion:

On the full `COCO val2017` set, repeated JPEG recompression provides a more favorable trade-off between storage efficiency and `YOLOv8n` detection performance than uniform bit-depth reduction stored in `PNG`.

A more precise formulation is:
moderate bit-depth reduction can preserve task-relevant information, but under the tested `BPC + PNG` scheme it is less efficient than JPEG recompression in the relationship between storage size and object detection quality.

## 9. Most Important Points for the Paper

The most informative operating points are:

- `q94` — near-baseline quality with clearly reduced size
- `q88` — almost baseline quality at roughly half the original storage size
- `q75` — strong practical compromise
- `b7` — an important negative result: baseline-level quality but much worse storage efficiency
- `b4` — the main BPC threshold point
- `q25` versus `b2` — a very strong comparison in the aggressive compression regime

These points are especially useful because they show not only a winning branch, but also why the competing branch loses in practical storage-performance terms.

## 10. Careful Interpretation

Some claims should still be phrased cautiously:

- `b7` being very slightly above `original` in `mAP50` does not mean it is better than the original; the two should be interpreted as practically equivalent
- `q94` and `q88` should be described as near-baseline, not lossless
- the result currently applies to:
  - one model (`YOLOv8n`)
  - one dataset (`COCO val2017`)
  - one BPC implementation (`uniform RGB bit-depth reduction + PNG`)
  - one fixed validation setup

## 11. Limitations

These limitations should be stated explicitly:

- only one detector was evaluated: `YOLOv8n`
- only one dataset was used: `COCO val2017`
- only one BPC storage implementation was tested
- JPEG recompression was applied to images that were already stored as JPEG
- no `PSNR` or `SSIM` analysis is included yet
- the diagnostic `MPS` attempts were unstable, so the final official experiment was conducted on CPU

## 12. Final Summary

The `val5k` experiment can now be treated as the main finished experiment of the current project.

It shows a clear and reproducible pattern:

- JPEG degradation is gradual and storage-efficient
- BPC degradation is also predictable, but in the tested `PNG`-based form it is not competitive in storage efficiency
- the strongest practical JPEG regimes are `q94`, `q88`, and `q75`
- the BPC branch remains scientifically informative, especially through `b7` and `b4`, but does not outperform JPEG in the tested setup

This is strong material for the main results section of the paper.
