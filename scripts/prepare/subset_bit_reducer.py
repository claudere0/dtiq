import os
import numpy as np
from PIL import Image

def quantize_image(data, bits):
    levels = 2**bits - 1

    normalized = data / 255.0
    quantized = np.round(normalized * levels)
    restored = (quantized / levels) * 255.0

    return np.clip(restored, 0, 255).astype(np.uint8)

def process_folder(input_folder, output_root="results", bits_range=range(1, 8)):
    folder_name = os.path.basename(os.path.normpath(input_folder))

    for bits in bits_range:
        # Check FileNotFoundError
        if not os.path.exists(input_folder):
            print(f"Error: Input folder '{input_folder}' not found!")
            return
        # skip 6 and 5 bit per channel
        if bits in (5, 6):
            print(f"Skip {bits} bpc...")
            continue
        # bit depth folder
        output_dir = os.path.join(f"{output_root}/b{bits}", f"val500_{bits}bpc/images")
        os.makedirs(output_dir, exist_ok=True)

        print(f"\n ~Processing {bits} bpc → {output_dir}")

        for file in os.listdir(input_folder):
            if not file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")):
                continue

            input_path = os.path.join(input_folder, file)

            img = Image.open(input_path).convert("RGB")
            data = np.array(img, dtype=np.float32)

            reduced_data = quantize_image(data, bits)
            final_img = Image.fromarray(reduced_data.astype("uint8"))

            base_name = os.path.splitext(file)[0]
            save_path = os.path.join(output_dir, f"{base_name}.png")
            final_img.save(save_path, format="PNG")

        print(f"Done {bits} bpc")

if __name__ == "__main__":
    process_folder("data/processed/original/val500/images/original_1_10th", "data/processed/bpc")