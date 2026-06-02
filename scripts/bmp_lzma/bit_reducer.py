import argparse
import shutil
import io
import lzma
from pathlib import Path

import numpy as np
from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
DEFAULT_BITS = [7, 4, 3, 2, 1]

def parse_args():
    parser = argparse.ArgumentParser(description="Generate bit-depth reduced dataset variants (.lzma).")
    parser.add_argument(
        "--source-images-dir",
        default="data/processed/val5k/original/images/val2017",
        help="Directory with source images.",
    )
    parser.add_argument(
        "--source-labels-dir",
        default="data/processed/val5k/original/labels/val2017",
        help="Directory with YOLO labels matching the source images.",
    )
    parser.add_argument("--output-root", default="data/processed/val5k/bpc_lzma", help="Output root for variants.")
    parser.add_argument(
        "--bits",
        nargs="*",
        type=int,
        default=DEFAULT_BITS,
        help="Bit-per-channel variants to generate.",
    )
    return parser.parse_args()

def quantize_image(data, bits):
    levels = (2**bits) - 1
    normalized = data / 255.0
    quantized = np.round(normalized * levels)
    restored = (quantized / levels) * 255.0
    return np.clip(restored, 0, 255).astype(np.uint8)

def copy_labels(source_labels_dir, destination_labels_dir):
    destination_labels_dir.mkdir(parents=True, exist_ok=True)
    for label_path in source_labels_dir.glob("*.txt"):
        shutil.copy2(label_path, destination_labels_dir / label_path.name)

def process_variant(source_images_dir, source_labels_dir, output_root, bits):
    variant_root = output_root / f"b{bits}"
    images_dir = variant_root / "images"
    labels_dir = variant_root / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    copy_labels(source_labels_dir, labels_dir)

    print(f"Processing {bits} bpc -> {images_dir}")
    total_size_bytes = 0
    
    for file_path in sorted(source_images_dir.iterdir()):
        if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        
        # Open image and convert to float array
        img = Image.open(file_path).convert("RGB")
        data = np.array(img, dtype=np.float32)
        
        # Apply quantization
        reduced_data = quantize_image(data, bits)
        
        # Convert to raw BMP in memory
        bmp_io = io.BytesIO()
        Image.fromarray(reduced_data).save(bmp_io, format="BMP")
        bmp_bytes = bmp_io.getvalue()
        
        # Compress with LZMA
        compressed_bytes = lzma.compress(bmp_bytes, preset=6)
        
        # Save as individual .lzma file
        save_path = images_dir / f"{file_path.stem}.lzma"
        with open(save_path, "wb") as f:
            f.write(compressed_bytes)
            
        total_size_bytes += save_path.stat().st_size

    total_size_mb = total_size_bytes / (1024 * 1024)
    print(f"Total size for {bits} bpc variant: {total_size_mb:.2f} MB")

def main():
    args = parse_args()
    source_images_dir = Path(args.source_images_dir)
    source_labels_dir = Path(args.source_labels_dir)
    output_root = Path(args.output_root)
    if not source_images_dir.exists():
        raise SystemExit(f"Source images directory not found: {source_images_dir}")
    if not source_labels_dir.exists():
        raise SystemExit(f"Source labels directory not found: {source_labels_dir}")

    for bits in args.bits:
        process_variant(source_images_dir, source_labels_dir, output_root, bits)

if __name__ == "__main__":
    main()
