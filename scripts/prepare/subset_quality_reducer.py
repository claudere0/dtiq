import argparse
import shutil
from pathlib import Path

from PIL import Image


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
DEFAULT_QUALITIES = [94, 88, 75, 50, 25]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate JPEG recompression dataset variants.")
    parser.add_argument(
        "--source-images-dir",
        default="data/processed/val500/original/images/original_1_10th",
        help="Directory with source images.",
    )
    parser.add_argument(
        "--source-labels-dir",
        default="data/processed/val500/original/labels/original_1_10th",
        help="Directory with YOLO labels matching the source images.",
    )
    parser.add_argument(
        "--output-root",
        default="data/processed/val500/jpeg",
        help="Output root for JPEG variants.",
    )
    parser.add_argument(
        "--qualities",
        nargs="*",
        type=int,
        default=DEFAULT_QUALITIES,
        help="JPEG quality variants to generate.",
    )
    return parser.parse_args()


def copy_labels(source_labels_dir, destination_labels_dir):
    destination_labels_dir.mkdir(parents=True, exist_ok=True)
    for label_path in source_labels_dir.glob("*.txt"):
        shutil.copy2(label_path, destination_labels_dir / label_path.name)


def process_variant(source_images_dir, source_labels_dir, output_root, quality):
    variant_root = output_root / f"q{quality}"
    images_dir = variant_root / "images"
    labels_dir = variant_root / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    copy_labels(source_labels_dir, labels_dir)

    print(f"Processing JPEG q{quality} -> {images_dir}")
    for file_path in sorted(source_images_dir.iterdir()):
        if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        img = Image.open(file_path).convert("RGB")
        save_path = images_dir / f"{file_path.stem}.jpg"
        img.save(save_path, format="JPEG", quality=quality, optimize=True)


def main():
    args = parse_args()
    source_images_dir = Path(args.source_images_dir)
    source_labels_dir = Path(args.source_labels_dir)
    output_root = Path(args.output_root)
    if not source_images_dir.exists():
        raise SystemExit(f"Source images directory not found: {source_images_dir}")
    if not source_labels_dir.exists():
        raise SystemExit(f"Source labels directory not found: {source_labels_dir}")

    for quality in args.qualities:
        process_variant(source_images_dir, source_labels_dir, output_root, quality)


if __name__ == "__main__":
    main()
