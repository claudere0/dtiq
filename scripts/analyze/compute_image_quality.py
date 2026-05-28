import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path

import cv2
import numpy as np
import yaml
from PIL import Image
from scipy.ndimage import gaussian_filter

try:
    from skimage.metrics import peak_signal_noise_ratio, structural_similarity
except ImportError:  # pragma: no cover - optional dependency fallback
    peak_signal_noise_ratio = None
    structural_similarity = None


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute PSNR and SSIM for all variants in an experiment config."
    )
    parser.add_argument(
        "--experiment-config",
        required=True,
        help="Path to configs/experiment_500.yaml or configs/experiment_5k.yaml.",
    )
    parser.add_argument(
        "--variants",
        nargs="*",
        default=None,
        help="Optional subset of non-original variants to process.",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Number of parallel worker threads for per-image metric computation.",
    )
    return parser.parse_args()


def load_yaml(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def resolve_images_dir(dataset_config_path):
    dataset = load_yaml(dataset_config_path)
    dataset_path = Path(dataset["path"])
    val_rel = Path(dataset["val"])
    return dataset_path / val_rel


def build_image_map(images_dir):
    image_map = {}
    for file_path in sorted(images_dir.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_map[file_path.stem] = file_path
    return image_map


def load_rgb_array(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


def fallback_psnr(original, variant):
    mse = np.mean((original - variant) ** 2, dtype=np.float64)
    if mse == 0:
        return float("inf")
    return float(20.0 * np.log10(255.0) - 10.0 * np.log10(mse))


def fallback_ssim(original, variant):
    original = original.astype(np.float64)
    variant = variant.astype(np.float64)
    c1 = (0.01 * 255.0) ** 2
    c2 = (0.03 * 255.0) ** 2
    channel_scores = []
    for channel in range(original.shape[2]):
        x = original[:, :, channel]
        y = variant[:, :, channel]
        mu_x = gaussian_filter(x, sigma=1.5)
        mu_y = gaussian_filter(y, sigma=1.5)
        mu_x_sq = mu_x * mu_x
        mu_y_sq = mu_y * mu_y
        mu_xy = mu_x * mu_y

        sigma_x_sq = gaussian_filter(x * x, sigma=1.5) - mu_x_sq
        sigma_y_sq = gaussian_filter(y * y, sigma=1.5) - mu_y_sq
        sigma_xy = gaussian_filter(x * y, sigma=1.5) - mu_xy

        numerator = (2 * mu_xy + c1) * (2 * sigma_xy + c2)
        denominator = (mu_x_sq + mu_y_sq + c1) * (sigma_x_sq + sigma_y_sq + c2)
        channel_scores.append(np.mean(numerator / denominator, dtype=np.float64))
    return float(np.mean(channel_scores, dtype=np.float64))


def fast_fallback_ssim(original, variant):
    original = original.astype(np.float64)
    variant = variant.astype(np.float64)
    c1 = (0.01 * 255.0) ** 2
    c2 = (0.03 * 255.0) ** 2
    channel_scores = []
    for channel in range(original.shape[2]):
        x = original[:, :, channel]
        y = variant[:, :, channel]
        mu_x = cv2.GaussianBlur(x, (11, 11), 1.5)
        mu_y = cv2.GaussianBlur(y, (11, 11), 1.5)
        mu_x_sq = mu_x * mu_x
        mu_y_sq = mu_y * mu_y
        mu_xy = mu_x * mu_y

        sigma_x_sq = cv2.GaussianBlur(x * x, (11, 11), 1.5) - mu_x_sq
        sigma_y_sq = cv2.GaussianBlur(y * y, (11, 11), 1.5) - mu_y_sq
        sigma_xy = cv2.GaussianBlur(x * y, (11, 11), 1.5) - mu_xy

        numerator = (2 * mu_xy + c1) * (2 * sigma_xy + c2)
        denominator = (mu_x_sq + mu_y_sq + c1) * (sigma_x_sq + sigma_y_sq + c2)
        channel_scores.append(np.mean(numerator / denominator, dtype=np.float64))
    return float(np.mean(channel_scores, dtype=np.float64))


def compute_pair_metrics(original_path, variant_path):
    original = load_rgb_array(original_path)
    variant = load_rgb_array(variant_path)
    if peak_signal_noise_ratio is not None and structural_similarity is not None:
        psnr = peak_signal_noise_ratio(original, variant, data_range=255.0)
        ssim = structural_similarity(original, variant, channel_axis=-1, data_range=255.0)
    else:
        psnr = cv2.PSNR(original.astype(np.uint8), variant.astype(np.uint8))
        ssim = fast_fallback_ssim(original, variant)
    return float(psnr), float(ssim)


def compute_one_pair(stem, original_path, variant_path):
    psnr, ssim = compute_pair_metrics(original_path, variant_path)
    return {
        "image_name": stem,
        "original_path": str(original_path),
        "variant_path": str(variant_path),
        "psnr": round(psnr, 6),
        "ssim": round(ssim, 6),
    }


def summarize_metric(values):
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(array.mean()),
        "std": float(array.std(ddof=0)),
        "min": float(array.min()),
        "max": float(array.max()),
    }


def write_per_image_csv(path, rows):
    fieldnames = ["image_name", "original_path", "variant_path", "psnr", "ssim"]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    experiment = load_yaml(args.experiment_config)
    results_root = Path(experiment["results_root"])
    quality_dir = results_root / "quality"
    summary_dir = results_root / "summary"
    quality_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)

    original_variant = next(
        (variant for variant in experiment["variants"] if variant["quantization_type"] == "original"),
        None,
    )
    if original_variant is None:
        raise SystemExit("Experiment config must contain an original baseline variant.")

    original_images_dir = resolve_images_dir(original_variant["dataset"])
    original_map = build_image_map(original_images_dir)
    selected_variants = set(args.variants) if args.variants else None

    summary_rows = []
    for variant in experiment["variants"]:
        if variant["quantization_type"] == "original":
            continue
        if selected_variants is not None and variant["name"] not in selected_variants:
            continue

        variant_images_dir = resolve_images_dir(variant["dataset"])
        variant_map = build_image_map(variant_images_dir)
        common_stems = sorted(set(original_map) & set(variant_map))
        if not common_stems:
            print(f"Skipping {variant['name']}: no shared image stems found.")
            continue

        per_image_rows = []
        print(f"Computing image quality for {variant['name']} over {len(common_stems)} images")
        if args.jobs > 1:
            max_workers = min(args.jobs, os.cpu_count() or 1)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(compute_one_pair, stem, original_map[stem], variant_map[stem])
                    for stem in common_stems
                ]
                for future in futures:
                    per_image_rows.append(future.result())
        else:
            for stem in common_stems:
                per_image_rows.append(compute_one_pair(stem, original_map[stem], variant_map[stem]))

        psnr_values = [row["psnr"] for row in per_image_rows]
        ssim_values = [row["ssim"] for row in per_image_rows]

        per_image_path = quality_dir / f"original_vs_{variant['name']}_per_image.csv"
        write_per_image_csv(per_image_path, per_image_rows)

        psnr_stats = summarize_metric(psnr_values)
        ssim_stats = summarize_metric(ssim_values)
        summary_rows.append(
            {
                "variant": variant["name"],
                "quantization_type": variant["quantization_type"],
                "parameter": variant["parameter"],
                "original_images_dir": str(original_images_dir),
                "variant_images_dir": str(variant_images_dir),
                "num_images": len(common_stems),
                "mean_psnr": round(psnr_stats["mean"], 6),
                "std_psnr": round(psnr_stats["std"], 6),
                "min_psnr": round(psnr_stats["min"], 6),
                "max_psnr": round(psnr_stats["max"], 6),
                "mean_ssim": round(ssim_stats["mean"], 6),
                "std_ssim": round(ssim_stats["std"], 6),
                "min_ssim": round(ssim_stats["min"], 6),
                "max_ssim": round(ssim_stats["max"], 6),
                "per_image_csv": str(per_image_path),
            }
        )

    output_csv = summary_dir / "image_quality.csv"
    fieldnames = [
        "variant",
        "quantization_type",
        "parameter",
        "original_images_dir",
        "variant_images_dir",
        "num_images",
        "mean_psnr",
        "std_psnr",
        "min_psnr",
        "max_psnr",
        "mean_ssim",
        "std_ssim",
        "min_ssim",
        "max_ssim",
        "per_image_csv",
    ]
    with output_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Saved image quality summary to {output_csv}")


if __name__ == "__main__":
    main()
