"""Download the Nomad ABM input data bundle from Zenodo.

Idempotent: skips the download if the zip is already present and its
SHA-256 matches the expected value. Extracts the zip into ``Data/``.

Run from the repo root::

    python scripts/download_data.py

After the script finishes, ``Data/`` will contain the five input
files the model expects: ``yearly_data_10_25.h5``,
``per_data_10_25.h5``, ``ext_raster.npy``, ``place_raster.npy``, and
``P_for_calib.shp`` (with sidecars).
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path


# ===== Filled in after the Zenodo upload — replace the three placeholders =====
# Once you publish to Zenodo and have the record ID + bundle SHA-256, set:
#   ZENODO_RECORD_ID = "12345678"        ← the trailing digits of the Zenodo URL
#   BUNDLE_FILENAME  = "nomad-abm-data-v1.0.zip"
#   BUNDLE_SHA256    = "<paste the sha256 printed by build_data_bundle.py>"
ZENODO_RECORD_ID: str | None = None
BUNDLE_FILENAME: str = "nomad-abm-data-v1.0.zip"
BUNDLE_SHA256: str | None = None
# ==============================================================================


REPO = Path(__file__).resolve().parent.parent
DATA_DIR = REPO / "Data"


def doi_url() -> str | None:
    if ZENODO_RECORD_ID is None:
        return None
    return f"https://doi.org/10.5281/zenodo.{ZENODO_RECORD_ID}"


def download_url() -> str | None:
    if ZENODO_RECORD_ID is None:
        return None
    return f"https://zenodo.org/records/{ZENODO_RECORD_ID}/files/{BUNDLE_FILENAME}?download=1"


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    if ZENODO_RECORD_ID is None or BUNDLE_SHA256 is None:
        sys.stderr.write(
            "ERROR: Zenodo record ID / bundle SHA-256 not configured.\n"
            "       Edit scripts/download_data.py and fill in the placeholders.\n"
            "       Until Phase 9 lands, get the data directly from the author.\n"
        )
        return 2

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DATA_DIR / BUNDLE_FILENAME

    if zip_path.exists():
        actual = sha256_file(zip_path)
        if actual == BUNDLE_SHA256:
            print(f"Bundle already present at {zip_path} (sha256 ok); skipping download.")
        else:
            print(f"Bundle at {zip_path} has wrong sha256; re-downloading.")
            zip_path.unlink()

    if not zip_path.exists():
        url = download_url()
        print(f"Downloading {url}")
        print(f"        →  {zip_path}")
        with urllib.request.urlopen(url) as resp, zip_path.open("wb") as out:
            shutil.copyfileobj(resp, out)
        actual = sha256_file(zip_path)
        if actual != BUNDLE_SHA256:
            sys.stderr.write(
                f"ERROR: downloaded bundle checksum mismatch.\n"
                f"  expected: {BUNDLE_SHA256}\n"
                f"  actual:   {actual}\n"
                f"  path:     {zip_path}\n"
            )
            return 1
        print("Checksum verified.")

    print(f"Extracting into {DATA_DIR}")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(DATA_DIR)

    # Files unpack into Data/nomad-abm-data-v<version>/<file>. Move them
    # up one level so the model's default paths resolve without any env
    # var fiddling.
    extracted_dirs = [p for p in DATA_DIR.iterdir() if p.is_dir() and p.name.startswith("nomad-abm-data-")]
    for d in extracted_dirs:
        for child in d.iterdir():
            target = DATA_DIR / child.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(child), str(target))
        d.rmdir()

    print()
    print(f"Done. Data ready under {DATA_DIR}/.")
    print(f"DOI: {doi_url()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
