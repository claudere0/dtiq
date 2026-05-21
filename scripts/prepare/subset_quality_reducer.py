import os
import numpy as np
from PIL import Image

QUALITY_LEVELS = [94, 88, 75, 50, 25]

def process_folder_jpeg_quality(input_folder, output_root="results"):
    # folder_name = os.path.basename(os.path.normpath(input_folder))

    for q in QUALITY_LEVELS:
        output_dir = os.path.join(f"{output_root}", f"q{q}/images")
        os.makedirs(output_dir, exist_ok=True)

        print(f"\nProcessing JPEG quality {q} → {output_dir}")

        for file in os.listdir(input_folder):
            if not file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")):
                continue

            input_path = os.path.join(input_folder, file)

            img = Image.open(input_path).convert("RGB")

            base_name = os.path.splitext(file)[0]
            save_path = os.path.join(output_dir, f"{base_name}.jpg")

            # JPEG compression
            img.save(
                save_path,
                format="JPEG",
                quality=q,
                optimize=True
            )

        print(f"Done quality {q}")

if __name__ == "__main__":
    process_folder_jpeg_quality(
        "data/processed/val500/original/images/original_1_10th",
        "data/processed/val500/jpeg"
    )