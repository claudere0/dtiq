import argparse
import json
import os
import sys
import time
from pathlib import Path

MATPLOTLIB_CACHE = Path(".cache/matplotlib").resolve()
MATPLOTLIB_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MATPLOTLIB_CACHE))

from ultralytics import YOLO


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()


def parse_args():
    parser = argparse.ArgumentParser(description="Run a single YOLO validation experiment.")
    parser.add_argument("--dataset", required=True, help="Path to dataset YAML.")
    parser.add_argument("--variant", required=True, help="Variant name, for example original or q94.")
    parser.add_argument("--experiment-name", required=True, help="Experiment group name, for example val500.")
    parser.add_argument("--quantization-type", required=True, help="original, jpeg or bpc.")
    parser.add_argument("--parameter", required=True, help="Variant parameter, for example 94 or 4.")
    parser.add_argument("--model", default="yolov8n.pt", help="Path to YOLO weights.")
    parser.add_argument("--device", default="cpu", help="Ultralytics device string.")
    parser.add_argument("--imgsz", type=int, default=640, help="Validation image size.")
    parser.add_argument("--batch", type=int, default=1, help="Validation batch size.")
    parser.add_argument("--workers", type=int, default=0, help="Number of dataloader workers.")
    parser.add_argument(
        "--results-root",
        required=True,
        help="Root directory for experiment outputs, for example results/val500.",
    )
    parser.add_argument("--exist-ok", action="store_true", help="Reuse existing YOLO run directory.")
    return parser.parse_args()


def ensure_dirs(results_root):
    results_root.mkdir(parents=True, exist_ok=True)
    (results_root / "console_log").mkdir(parents=True, exist_ok=True)
    (results_root / "metrics").mkdir(parents=True, exist_ok=True)
    (results_root / "yolo_runs").mkdir(parents=True, exist_ok=True)


def build_metrics_payload(args, metrics, elapsed_seconds):
    return {
        "experiment_name": args.experiment_name,
        "variant": args.variant,
        "quantization_type": args.quantization_type,
        "parameter": args.parameter,
        "dataset": args.dataset,
        "model": args.model,
        "device": args.device,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "save_dir": str(metrics.save_dir),
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "map50": float(metrics.box.map50),
        "map50_95": float(metrics.box.map),
        "fitness": float(metrics.fitness),
    }


def run_validation(args):
    results_root = Path(args.results_root)
    ensure_dirs(results_root)

    log_path = results_root / "console_log" / f"{args.variant}.txt"
    metrics_path = results_root / "metrics" / f"{args.variant}.json"

    model = YOLO(args.model)
    yolo_project = (results_root / "yolo_runs").resolve()

    with log_path.open("w", encoding="utf-8") as log_file:
        tee = Tee(sys.__stdout__, log_file)
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        start_time = time.perf_counter()
        try:
            sys.stdout = tee
            sys.stderr = tee
            print(f"Running experiment '{args.experiment_name}' for variant '{args.variant}'")
            print(f"Dataset config: {args.dataset}")
            metrics = model.val(
                data=args.dataset,
                imgsz=args.imgsz,
                batch=args.batch,
                workers=args.workers,
                device=args.device,
                project=str(yolo_project),
                name=args.variant,
                exist_ok=args.exist_ok,
            )
            elapsed_seconds = time.perf_counter() - start_time
            payload = build_metrics_payload(args, metrics, elapsed_seconds)
            print("mAP50-95:", payload["map50_95"])
            print("mAP50:", payload["map50"])
            print("Precision:", payload["precision"])
            print("Recall:", payload["recall"])
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    metrics_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved metrics to {metrics_path}")
    return payload


def main():
    args = parse_args()
    run_validation(args)


if __name__ == "__main__":
    main()
