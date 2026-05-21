import argparse
import subprocess
import sys
from pathlib import Path

import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="Run every validation listed in an experiment config.")
    parser.add_argument(
        "--experiment-config",
        required=True,
        help="Path to configs/experiment_500.yaml or configs/experiment_5k.yaml.",
    )
    parser.add_argument(
        "--variants",
        nargs="*",
        default=None,
        help="Optional subset of variants to run, for example original q94 q88.",
    )
    parser.add_argument("--exist-ok", action="store_true", help="Reuse existing YOLO run directories.")
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue with the next variant when one run fails.",
    )
    return parser.parse_args()


def load_experiment_config(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def iter_variants(config, requested_variants):
    allowed = set(requested_variants) if requested_variants else None
    for variant in config["variants"]:
        if allowed is None or variant["name"] in allowed:
            yield variant


def build_command(config, variant, exist_ok):
    script_path = Path(__file__).resolve().parent / "run_yolo_val.py"
    command = [
        sys.executable,
        str(script_path),
        "--dataset",
        variant["dataset"],
        "--variant",
        variant["name"],
        "--experiment-name",
        config["experiment_name"],
        "--quantization-type",
        str(variant["quantization_type"]),
        "--parameter",
        str(variant["parameter"]),
        "--model",
        config["model"],
        "--device",
        str(config["device"]),
        "--imgsz",
        str(config["imgsz"]),
        "--batch",
        str(config["batch"]),
        "--workers",
        str(config["workers"]),
        "--results-root",
        config["results_root"],
    ]
    if exist_ok:
        command.append("--exist-ok")
    return command


def main():
    args = parse_args()
    config = load_experiment_config(args.experiment_config)

    failures = []
    selected_variants = list(iter_variants(config, args.variants))
    if not selected_variants:
        raise SystemExit("No variants matched the provided filter.")

    for variant in selected_variants:
        print(f"Starting variant: {variant['name']}")
        command = build_command(config, variant, args.exist_ok)
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            failures.append(variant["name"])
            print(f"Variant failed: {variant['name']}")
            if not args.continue_on_error:
                break

    if failures:
        raise SystemExit(f"Validation failed for variants: {', '.join(failures)}")

    print(f"Completed {len(selected_variants)} validation runs from {args.experiment_config}")


if __name__ == "__main__":
    main()
