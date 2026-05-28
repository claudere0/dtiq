import argparse
import csv
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Create a short markdown summary from image_quality.csv.")
    parser.add_argument(
        "--image-quality-csv",
        required=True,
        help="Path to the CSV created by compute_image_quality.py.",
    )
    return parser.parse_args()


def load_rows(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def best_by(rows, key):
    return max(rows, key=lambda row: float(row[key]))


def format_row(label, row):
    return (
        f"- {label}: {row['variant']} | "
        f"PSNR={float(row['mean_psnr']):.3f} | SSIM={float(row['mean_ssim']):.4f}"
    )


def main():
    args = parse_args()
    rows = load_rows(args.image_quality_csv)
    if not rows:
        raise SystemExit("image_quality.csv is empty.")

    jpeg_rows = [row for row in rows if row["quantization_type"] == "jpeg"]
    bpc_rows = [row for row in rows if row["quantization_type"] == "bpc"]

    lines = ["# Image Quality Summary", ""]
    if jpeg_rows:
        lines.append(format_row("Best JPEG by mean PSNR", best_by(jpeg_rows, "mean_psnr")))
        lines.append(format_row("Best JPEG by mean SSIM", best_by(jpeg_rows, "mean_ssim")))
    if bpc_rows:
        lines.append(format_row("Best BPC by mean PSNR", best_by(bpc_rows, "mean_psnr")))
        lines.append(format_row("Best BPC by mean SSIM", best_by(bpc_rows, "mean_ssim")))

    output_path = Path(args.image_quality_csv).with_name("image_quality_summary.md")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved image quality summary to {output_path}")


if __name__ == "__main__":
    main()
