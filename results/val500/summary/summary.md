# Experiment Summary

Pilot experiment: `500` images from `COCO val2017`, `YOLOv8n`, `device=mps`, `imgsz=640`, `batch=1`, `workers=0`.

## Baseline

- `original`: size=`77.1354 MB`, `mAP50=0.5591`, `mAP50-95=0.4056`

## Recommended JPEG Operating Points

- `q94`: near-baseline detection quality with storage reduction; size=`53.9552 MB`, compression=`1.43x`, `mAP50=0.5543`, `mAP50-95=0.4039`
- `q88`: strongest near-baseline pilot trade-off; size=`38.0456 MB`, compression=`2.03x`, `mAP50=0.5547`, `mAP50-95=0.4028`
- `q75`: strong practical compromise; size=`23.7281 MB`, compression=`3.25x`, `mAP50=0.5424`, `mAP50-95=0.3923`
- `q25`: most aggressive JPEG point; size=`9.4916 MB`, compression=`8.13x`, but detection loss is substantial (`mAP50=0.4419`)

## BPC Findings

- `b7`: best BPC by detection quality; `mAP50=0.5597`, `mAP50-95=0.4056`, but size=`189.5861 MB`, which is much larger than the original
- `b4`: main BPC threshold point; `mAP50=0.5358`, `mAP50-95=0.3843`, but size=`80.7269 MB`, so storage savings are absent
- `b2` and `b1`: aggressive BPC modes strongly degrade detection quality and are not practical operating points

## Image Quality

- Best JPEG by mean PSNR/SSIM: `q94` with `PSNR=37.7873`, `SSIM=0.9688`
- Best BPC by mean PSNR/SSIM: `b7` with `PSNR=51.2218`, `SSIM=0.9980`
- The pilot confirms that image similarity metrics and storage efficiency must be interpreted together with detection metrics

## Article-Level Conclusion

The pilot already shows the same structural pattern later confirmed by `val5k`: moderate JPEG recompression preserves detection quality while reducing storage, whereas the tested `BPC + PNG` branch preserves quality only in modes that do not reduce storage effectively.
