import shutil
from pathlib import Path


def main():
    source_images_dir = Path("data/raw/coco/images/val2017")
    source_labels_dir = Path("data/raw/coco/labels/val2017")
    destination_root = Path("data/processed/val5k/original")
    destination_images_dir = destination_root / "images" / "val2017"
    destination_labels_dir = destination_root / "labels" / "val2017"

    if not source_images_dir.exists():
        raise SystemExit(f"Source images directory not found: {source_images_dir}")
    if not source_labels_dir.exists():
        raise SystemExit(f"Source labels directory not found: {source_labels_dir}")

    if destination_images_dir.exists():
        shutil.rmtree(destination_images_dir)
    if destination_labels_dir.exists():
        shutil.rmtree(destination_labels_dir)

    destination_images_dir.parent.mkdir(parents=True, exist_ok=True)
    destination_labels_dir.parent.mkdir(parents=True, exist_ok=True)

    print(f"Copying {source_images_dir} -> {destination_images_dir}")
    shutil.copytree(source_images_dir, destination_images_dir)

    print(f"Copying {source_labels_dir} -> {destination_labels_dir}")
    shutil.copytree(source_labels_dir, destination_labels_dir)


if __name__ == "__main__":
    main()
