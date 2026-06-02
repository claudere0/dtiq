import shutil
from pathlib import Path

from PIL import Image


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
DEFAULT_QUALITIES = [94, 88, 75, 50, 25]


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
    source_images_dir = Path("data/processed/val5k/original/images/val2017")
    source_labels_dir = Path("data/processed/val5k/original/labels/val2017")
    output_root = Path("data/processed/val5k/jpeg")

    if not source_images_dir.exists():
        raise SystemExit(
            "Source images for val5k are missing. Run scripts/prepare/create_val5k_original.py first."
        )
    if not source_labels_dir.exists():
        raise SystemExit(
            "Source labels for val5k are missing. Run scripts/prepare/create_val5k_original.py first."
        )

    for quality in DEFAULT_QUALITIES:
        process_variant(source_images_dir, source_labels_dir, output_root, quality)


if __name__ == "__main__":
    main()
