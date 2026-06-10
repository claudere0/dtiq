# Final Table for Article

Final `val5k` experiment configuration:

- dataset: `COCO val2017` (`5000` images)
- model: `YOLOv8n`
- device: `cpu`
- image size: `640`
- batch: `1`
- workers: `0`

Important note:

- `original_long_mps_check` and `original_slow_one` in `results/val5k` were unsuccessful diagnostic runs on `device=mps`
- they are **not** part of the final experiment
- the final official results below are the CPU-based results from [metrics.csv](/Users/amirkarataev/Desktop/dissertation/dtiq/results/val5k/summary/metrics.csv:1)

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

## Key Article-Level Takeaways

- `q94` gives near-baseline detection quality while reducing dataset size substantially
- `q88` provides almost the same quality with approximately half the original storage size
- `q75` remains a strong practical compromise
- `b7` preserves detection quality but is much worse than the original in storage size
- `b4` is the main threshold point in the BPC branch
- `q25` remains much stronger than aggressive BPC modes in terms of `size vs mAP`
