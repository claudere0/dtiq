import argparse
import shutil
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def parse_args():
    parser = argparse.ArgumentParser(description="Create a YOLO subset from COCO images and labels.")
    parser.add_argument("--source-root", default="data/raw/coco", help="Root directory with images/ and labels/.")
    parser.add_argument("--source-split", default="val2017", help="Image and label split to copy.")
    parser.add_argument("--output-root", default="data/processed/val500/original", help="Output dataset root.")
    parser.add_argument(
        "--subset-name",
        default="original_1_10th",
        help="Subdirectory name under output images/ and labels/.",
    )
    parser.add_argument(
        "--num-images",
        type=int,
        default=500,
        help="Number of sorted images to copy. Use 0 or a negative value to copy the full split.",
    )
    return parser.parse_args()


def select_images(source_images_dir, num_images):
    all_images = sorted(
        file_path.name
        for file_path in source_images_dir.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if num_images and num_images > 0:
        return all_images[:num_images]
    return all_images


def create_subset(args):
    source_root = Path(args.source_root)
    source_images_dir = source_root / "images" / args.source_split
    source_labels_dir = source_root / "labels" / args.source_split

    destination_root = Path(args.output_root)
    destination_images_dir = destination_root / "images" / args.subset_name
    destination_labels_dir = destination_root / "labels" / args.subset_name
    destination_images_dir.mkdir(parents=True, exist_ok=True)
    destination_labels_dir.mkdir(parents=True, exist_ok=True)

    selected_images = select_images(source_images_dir, args.num_images)
    copied_labels = 0

    print(f"Copying {len(selected_images)} images from {source_images_dir}")
    for image_name in selected_images:
        shutil.copy2(source_images_dir / image_name, destination_images_dir / image_name)
        label_name = f"{Path(image_name).stem}.txt"
        label_path = source_labels_dir / label_name
        if label_path.exists():
            shutil.copy2(label_path, destination_labels_dir / label_name)
            copied_labels += 1

    print(f"Images copied to {destination_images_dir}")
    print(f"Labels copied to {destination_labels_dir}: {copied_labels}")
    print(f"Background images without labels: {len(selected_images) - copied_labels}")


def main():
    args = parse_args()
    create_subset(args)


if __name__ == "__main__":
    main()
