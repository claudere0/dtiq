import subprocess
import sys
from pathlib import Path


SCRIPTS = [
    "create_val5k_original.py",
    "create_val5k_jpeg_variants.py",
    "create_val5k_bpc_variants.py",
]


def main():
    prepare_dir = Path(__file__).resolve().parent
    for script_name in SCRIPTS:
        script_path = prepare_dir / script_name
        print(f"Running {script_path.name}")
        subprocess.run([sys.executable, str(script_path)], check=True)


if __name__ == "__main__":
    main()
