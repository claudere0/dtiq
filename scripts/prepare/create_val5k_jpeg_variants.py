from pathlib import Path

from subset_quality_reducer import DEFAULT_QUALITIES, process_variant


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
