import os
import shutil
from pathlib import Path

base_dir = Path("./data/raw/coco")
prcsd_dir = Path("./data/processed/original/val500")

src_img_dir = base_dir / "images" / "val2017"
src_lbl_dir = base_dir / "labels" / "val2017"

dst_img_dir = prcsd_dir / "images" / "original_1_10th" #create if not work
dst_lbl_dir = prcsd_dir / "labels" / "original_1_10th" #create if not work

def create_yolo_subset(num_images=500):
    # create if does not exist
    dst_img_dir.mkdir(parents=True, exist_ok=True)
    dst_lbl_dir.mkdir(parents=True, exist_ok=True)

    # sorted list of images
    all_images = sorted([f for f in os.listdir(src_img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    # only first 500
    subset_images = all_images[:num_images]
    
    copied_images_count = 0
    copied_labels_count = 0

    print(f"Start copying first {num_images} images...")

    for img_name in subset_images:
        # 1. copy image
        src_img_path = src_img_dir / img_name
        dst_img_path = dst_img_dir / img_name
        shutil.copy2(src_img_path, dst_img_path)
        copied_images_count += 1

        # 2. find same annotation file (change to .txt)
        label_name = Path(img_name).stem + ".txt"
        src_lbl_path = src_lbl_dir / label_name
        dst_lbl_path = dst_lbl_dir / label_name

        if src_lbl_path.exists():
            shutil.copy2(src_lbl_path, dst_lbl_path)
            copied_labels_count += 1

    print("---")
    print(f"Succesfully copied images to '{dst_img_dir.name}': {copied_images_count}")
    print(f"Succesfully copied annotations to '{dst_lbl_dir.name}': {copied_labels_count}")
    print(f"Skipped background images (without .txt): {copied_images_count - copied_labels_count}")

if __name__ == "__main__":
    create_yolo_subset(num_images=500)