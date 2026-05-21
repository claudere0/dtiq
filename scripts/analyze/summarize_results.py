import argparse
import csv
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Create a short textual summary from metrics.csv.")
    parser.add_argument("--metrics-csv", required=True, help="Path to the CSV created by collect_metrics.py.")
    return parser.parse_args()


def load_rows(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def to_float(row, key):
    return float(row[key])


def best_by(rows, metric_key):
    return max(rows, key=lambda row: to_float(row, metric_key))


def best_tradeoff(rows):
    return max(rows, key=lambda row: to_float(row, "map50") / max(to_float(row, "dataset_size_mb"), 1e-9))


def format_row(label, row):
    return (
        f"- {label}: {row['variant']} | size={row['dataset_size_mb']} MB | "
        f"mAP50={float(row['map50']):.3f} | mAP50-95={float(row['map50_95']):.3f}"
    )


def main():
    args = parse_args()
    rows = load_rows(args.metrics_csv)
    if not rows:
        raise SystemExit("metrics.csv is empty.")

    baseline = next((row for row in rows if row["quantization_type"] == "original"), None)
    jpeg_rows = [row for row in rows if row["quantization_type"] == "jpeg"]
    bpc_rows = [row for row in rows if row["quantization_type"] == "bpc"]

    lines = ["# Experiment Summary", ""]
    if baseline:
        lines.append(format_row("Baseline", baseline))
    if jpeg_rows:
        lines.append(format_row("Best JPEG by mAP50", best_by(jpeg_rows, "map50")))
        lines.append(format_row("Best JPEG size-to-mAP50 trade-off", best_tradeoff(jpeg_rows)))
    if bpc_rows:
        lines.append(format_row("Best BPC by mAP50", best_by(bpc_rows, "map50")))
        lines.append(format_row("Best BPC size-to-mAP50 trade-off", best_tradeoff(bpc_rows)))

    output_path = Path(args.metrics_csv).with_name("summary.md")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved summary to {output_path}")


if __name__ == "__main__":
    main()
