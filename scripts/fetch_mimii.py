"""Download and extract a MIMII dataset archive from Zenodo into data/.

Usage:

    python scripts/fetch_mimii.py --type fan --snr 6
    python scripts/fetch_mimii.py --type valve --snr -6 --keep-zip

Result: data/<snr>_dB/<type>/...
"""

import argparse
import sys
import urllib.request
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MACHINE_TYPES = ["fan", "pump", "slider", "valve"]
SNRS = ["-6", "0", "6"]


def download(url: str, dest: Path) -> None:
    def report(blocks: int, block_size: int, total: int) -> None:
        done = blocks * block_size
        pct = f"{done / total:5.1%}" if total > 0 else "?"
        print(f"\r  {pct}  {done / 1e9:6.2f} GB", end="", flush=True)

    urllib.request.urlretrieve(url, dest, reporthook=report)
    print()


def extract(zip_path: Path, snr_dir: str, data_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        # normalise paths
        rooted = zf.namelist()[0].startswith(snr_dir)
        zf.extractall(data_dir if rooted else data_dir / snr_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--type", choices=MACHINE_TYPES, required=True, dest="machine")
    parser.add_argument("--snr", choices=SNRS, required=True, help="SNR in dB")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data")
    parser.add_argument("--keep-zip", action="store_true")
    args = parser.parse_args()

    snr_dir = f"{args.snr}_dB"
    target = args.data_dir / snr_dir / args.machine
    if target.exists():
        print(f"{target} already exists. delete it to re-fetch")
        return 1

    name = f"{snr_dir}_{args.machine}.zip"
    url = f"https://zenodo.org/records/3384388/files/{name}?download=1"
    zip_path = args.data_dir / name
    args.data_dir.mkdir(parents=True, exist_ok=True)

    print(f"downloading {name}")
    download(url, zip_path)

    print(f"extracting to {target}")
    extract(zip_path, snr_dir, args.data_dir)

    if not args.keep_zip:
        zip_path.unlink()
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
