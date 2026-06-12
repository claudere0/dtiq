import argparse
import csv
from pathlib import Path


DEFAULT_BITS = [7, 4, 3, 2, 1]
DEFAULT_ARTICLE_METRICS_CSV = Path("results/article_figures/article_metrics_table.csv")
DEFAULT_LZMA_ROOT = Path("data/processed/val5k/bpc_lzma")
DEFAULT_OUTPUT_CSV = Path("results/article_figures/lzma_storage.csv")
BMP_RAW_APPROX_MB = 4110.0


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize the auxiliary BMP+LZMA storage comparison.")
    parser.add_argument(
        "--article-metrics-csv",
        default=str(DEFAULT_ARTICLE_METRICS_CSV),
        help="Path to article_metrics_table.csv, used to read PNG sizes for the bpc variants.",
    )
    parser.add_argument(
        "--lzma-root",
        default=str(DEFAULT_LZMA_ROOT),
        help="Root directory containing b7/b4/b3/b2/b1 subdirectories with .lzma images.",
    )
    parser.add_argument(
        "--output-csv",
        default=str(DEFAULT_OUTPUT_CSV),
        help="Path for the generated lzma_storage.csv file.",
    )
    parser.add_argument(
        "--bits",
        nargs="*",
        type=int,
        default=DEFAULT_BITS,
        help="Bit-depth variants to summarize.",
    )
    return parser.parse_args()


def read_csv(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_png_sizes(article_metrics_csv):
    png_sizes = {}
    for row in read_csv(article_metrics_csv):
        variant = row["variant"]
        if variant.startswith("b") and variant != "b8":
            png_sizes[variant] = float(row["size_mb"])
    return png_sizes


def summarize_variant(variant_dir):
    image_dir = variant_dir / "images"
    if not image_dir.exists():
        raise SystemExit(f"Missing LZMA image directory: {image_dir}")

    lzma_files = sorted(image_dir.glob("*.lzma"))
    if not lzma_files:
        raise SystemExit(f"No .lzma files found in {image_dir}")

    compressed_bytes = 0
    for file_path in lzma_files:
        compressed_bytes += file_path.stat().st_size

    return {
        "lzma_mb": compressed_bytes / (1024 * 1024),
    }


def build_rows(article_metrics_csv, lzma_root, bits):
    png_sizes = load_png_sizes(article_metrics_csv)
    rows = []

    for bit_depth in bits:
        variant = f"b{bit_depth}"
        if variant not in png_sizes:
            raise SystemExit(f"PNG size for {variant} not found in {article_metrics_csv}")

        stats = summarize_variant(Path(lzma_root) / variant)
        png_mb = png_sizes[variant]
        lzma_mb = stats["lzma_mb"]
        rows.append(
            {
                "variant": variant,
                "bmp_raw_mb": BMP_RAW_APPROX_MB,
                "png_mb": png_mb,
                "lzma_mb": lzma_mb,
                "png_over_lzma": png_mb / lzma_mb,
            }
        )

    return rows


def write_csv(rows, output_csv):
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["variant", "bmp_raw_mb", "png_mb", "lzma_mb", "png_over_lzma"]
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: (row[key] if key == "variant" else round(row[key], 6)) for key in fieldnames})


def format_mb(value, digits=2):
    return f"{value:.{digits}f}"


def generate(article_metrics_csv, lzma_root, output_csv, bits):
    rows = build_rows(article_metrics_csv, lzma_root, bits)
    write_csv(rows, output_csv)
    return rows


def main():
    args = parse_args()
    generate(
        args.article_metrics_csv,
        args.lzma_root,
        args.output_csv,
        args.bits,
    )
    print(f"Saved LZMA summary to {args.output_csv}")


if __name__ == "__main__":
    main()
