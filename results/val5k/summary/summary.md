# Experiment Summary

Final experiment: `COCO val2017` (`5000` images), `YOLOv8n`, `device=cpu`, `imgsz=640`, `batch=1`, `workers=0`.

## Baseline

- `original`: size=`776.9634 MB`, `mAP50=0.5187`, `mAP50-95=0.3681`

## Recommended JPEG Operating Points

- `q94`: near-baseline detection quality with clear storage reduction; size=`543.3825 MB`, compression=`1.43x`, `mAP50=0.5162`, `mAP50-95=0.3660`
- `q88`: strongest near-baseline trade-off; size=`384.2208 MB`, compression=`2.02x`, `mAP50=0.5147`, `mAP50-95=0.3647`
- `q75`: strong practical compromise; size=`239.2142 MB`, compression=`3.25x`, `mAP50=0.5057`, `mAP50-95=0.3563`
- `q25`: most aggressive JPEG point; size=`95.9412 MB`, compression=`8.10x`, but detection loss is substantial (`mAP50=0.4073`)

## BPC Findings

- `b7`: best BPC by detection quality; `mAP50=0.5189`, `mAP50-95=0.3680`, but size=`1912.6668 MB`, which is much larger than the original
- `b4`: main BPC threshold point; `mAP50=0.4987`, `mAP50-95=0.3509`, but size=`816.7964 MB`, so storage savings are absent
- `b2` and `b1`: aggressive BPC modes strongly degrade detection quality and are not practical operating points

## Image Quality

- Best JPEG by mean PSNR/SSIM: `q94` with `PSNR=37.4721`, `SSIM=0.9677`
- Best BPC by mean PSNR/SSIM: `b7` with `PSNR=51.2191`, `SSIM=0.9980`
- High PSNR/SSIM alone does not guarantee a useful storage trade-off: `b7` preserves visual similarity but increases dataset size dramatically

## Article-Level Conclusion

For the tested `YOLOv8n + COCO val2017` setup, JPEG recompression is more effective than the current `BPC + PNG` scheme for reducing dataset size while preserving object detection quality. The strongest article-level points are `q88`, `q75`, `q94`, and the negative BPC result represented by `b7` and `b4`.
