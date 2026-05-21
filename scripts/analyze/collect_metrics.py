import argparse
import csv
import json
from pathlib import Path

import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="Collect per-variant metrics into a single CSV file.")
    parser.add_argument(
        "--experiment-config",
        required=True,
        help="Path to the experiment YAML used for validation runs.",
    )
    return parser.parse_args()


def load_yaml(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def resolve_images_dir(dataset_config_path):
    dataset = load_yaml(dataset_config_path)
    dataset_path = Path(dataset["path"])
    val_rel = Path(dataset["val"])
    return dataset_path / val_rel


def folder_size_mb(path):
    total_bytes = 0
    for file_path in path.rglob("*"):
        if file_path.is_file():
            total_bytes += file_path.stat().st_size
    return round(total_bytes / (1024 * 1024), 4)


def count_images(path):
    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    return sum(1 for file_path in path.rglob("*") if file_path.suffix.lower() in extensions)


def main():
    args = parse_args()
    experiment = load_yaml(args.experiment_config)
    results_root = Path(experiment["results_root"])
    metrics_dir = results_root / "metrics"
    summary_dir = results_root / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    output_csv = summary_dir / "metrics.csv"

    fieldnames = [
        "experiment_name",
        "variant",
        "quantization_type",
        "parameter",
        "dataset",
        "images_dir",
        "num_images",
        "dataset_size_mb",
        "model",
        "device",
        "imgsz",
        "batch",
        "workers",
        "elapsed_seconds",
        "precision",
        "recall",
        "map50",
        "map50_95",
        "fitness",
        "save_dir",
    ]

    rows = []
    for variant in experiment["variants"]:
        metrics_path = metrics_dir / f"{variant['name']}.json"
        if not metrics_path.exists():
            print(f"Skipping missing metrics file: {metrics_path}")
            continue

        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        images_dir = resolve_images_dir(variant["dataset"])
        row = {key: payload.get(key, "") for key in fieldnames}
        row["images_dir"] = str(images_dir)
        row["num_images"] = count_images(images_dir)
        row["dataset_size_mb"] = folder_size_mb(images_dir)
        rows.append(row)

    with output_csv.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved aggregated metrics to {output_csv}")


if __name__ == "__main__":
    main()
