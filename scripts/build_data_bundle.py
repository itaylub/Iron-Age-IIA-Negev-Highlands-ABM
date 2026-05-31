"""Build the Zenodo data bundle.

Bundles the five canonical input files (the two ``_10_25`` HDF5 files,
the two ``.npy`` masks, and the calibration shapefile + sidecars) into
a single versioned ``.zip`` ready for upload to Zenodo. Prints the
final SHA-256 so you can paste it into ``scripts/download_data.py``.

Read-only on the source files. Run from anywhere — it uses the same
``Data/`` discovery as ``scripts/inspect_data.py``::

    python scripts/build_data_bundle.py
    # → ./nomad-abm-data-v1.0.zip and a SHA-256 line you give Claude.

The flat layout inside the zip puts the calibration shapefile next to
the other inputs, so when ``scripts/download_data.py`` extracts the
bundle into ``Data/`` the file lands at ``Data/P_for_calib.shp``
(where the model's default ``CALIB_SHP_PATH`` looks) regardless of
the ``points_all/`` subdirectory on the data machine.
"""

from __future__ import annotations

import hashlib
import os
import sys
import zipfile
from pathlib import Path


BUNDLE_VERSION = "v1.0"
BUNDLE_BASENAME = f"nomad-abm-data-{BUNDLE_VERSION}"

# Source paths are resolved relative to Data/. The first existing
# entry from each tuple wins (lets the shapefile live in either
# Data/P_for_calib.shp or Data/points_all/P_for_calib.shp).
SOURCES: list[tuple[str, ...]] = [
    ("yearly_data_10_25.h5",),
    ("per_data_10_25.h5",),
    ("ext_raster.npy",),
    ("place_raster.npy",),
    ("P_for_calib.shp", "points_all/P_for_calib.shp"),
    ("P_for_calib.shx", "points_all/P_for_calib.shx"),
    ("P_for_calib.dbf", "points_all/P_for_calib.dbf"),
    ("P_for_calib.prj", "points_all/P_for_calib.prj"),
]


def _script_path() -> Path | None:
    try:
        return Path(__file__).resolve()
    except NameError:
        return None


def find_data_dir() -> Path:
    env = os.environ.get("NOMAD_ABM_DATA_DIR")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env))
    candidates.append(Path.cwd() / "Data")
    here = _script_path()
    if here is not None:
        for ancestor in (here.parent, here.parent.parent, here.parent.parent.parent):
            candidates.append(ancestor / "Data")
    candidates.append(Path("D:/itay/ABM/Data"))
    candidates.append(Path("/home/user/ABM/Data"))
    seen: set[Path] = set()
    for c in candidates:
        try:
            c = c.resolve()
        except OSError:
            continue
        if c in seen:
            continue
        seen.add(c)
        if c.is_dir():
            return c
    raise SystemExit(
        "ERROR: could not find Data/. Tried:\n  " + "\n  ".join(str(c) for c in seen)
    )


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def resolve_sources(data_dir: Path) -> list[tuple[str, Path]]:
    """Map each logical filename to its actual location on disk."""
    resolved: list[tuple[str, Path]] = []
    missing: list[str] = []
    for entry in SOURCES:
        target_name = Path(entry[0]).name  # name inside the zip
        chosen: Path | None = None
        for rel in entry:
            p = data_dir / rel
            if p.exists():
                chosen = p
                break
        if chosen is None:
            missing.append(" or ".join(str(data_dir / r) for r in entry))
        else:
            resolved.append((target_name, chosen))
    if missing:
        msg = "ERROR: missing required input files:\n  " + "\n  ".join(missing)
        raise SystemExit(msg)
    return resolved


def build_bundle(out_dir: Path, data_dir: Path) -> Path:
    out_path = out_dir / f"{BUNDLE_BASENAME}.zip"
    resolved = resolve_sources(data_dir)

    print(f"Building {out_path} from {data_dir}")
    total = 0
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for arcname, src in resolved:
            zf.write(src, f"{BUNDLE_BASENAME}/{arcname}")
            size = src.stat().st_size
            total += size
            print(f"  + {arcname:30s}  {size:>13,} bytes  ({src})")

    zip_size = out_path.stat().st_size
    digest = sha256_file(out_path)
    print()
    print(f"Bundle path : {out_path}")
    print(f"Input bytes : {total:,}")
    print(f"Zip bytes   : {zip_size:,}  (compression ratio {zip_size / total:.3f})")
    print(f"SHA-256     : {digest}")
    print()
    print("Next: upload the zip to Zenodo (docs/ZENODO_UPLOAD.md), then send")
    print("Claude the resulting DOI / record ID along with the SHA-256 above.")
    return out_path


def main() -> int:
    data_dir = find_data_dir()
    out_dir = Path.cwd()
    build_bundle(out_dir, data_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
