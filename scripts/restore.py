"""Restore the data files from their zips and verify every sha256.

Every data file under data/ is committed only as a deterministic zip plus a
.sha256 sidecar; data/SHA256SUMS pins the sha256 of every zip and of every file
restored from it. This script uses the standard library only.

Each zip is extracted into its own directory: a single-file zip such as
data/campaign/per_task.csv.zip restores data/campaign/per_task.csv, and the two
archives restore data/instrument/specs/ (47 .mop) and
data/baselines/cognicrypt/crysl-rules/ (49 .crysl).

Usage:
    python -m scripts.restore                 extract every zip, then verify
    python -m scripts.restore --verify-only   verify the restored files only
    python -m scripts.restore --clean         delete the restored files

Exit code 0 when every check passes, 1 on any mismatch or missing file.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SUMS = DATA / "SHA256SUMS"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def zips() -> list[Path]:
    return sorted(DATA.rglob("*.zip"))


def _target(z: Path, name: str) -> Path:
    """Where a zip entry lands; refuses an entry that escapes data/."""
    target = (z.parent / name).resolve()
    if name.startswith("/") or not target.is_relative_to(DATA):
        raise ValueError(f"{z.relative_to(DATA)}: entry {name!r} escapes data/")
    return target


def extract() -> int:
    """Extract every zip next to itself; return the number of files written."""
    n = 0
    for z in zips():
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                if name.endswith("/"):
                    continue  # the zips hold no directory entries; skip any defensively
                target = _target(z, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(name))
                n += 1
    return n


def _check_list(listing: Path, base: Path) -> tuple[int, list[str]]:
    """Check one sha256sum-format file; names are relative to ``base``."""
    ok, problems = 0, []
    for line in listing.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, name = line.split(None, 1)
        p = base / name.strip()
        label = p.relative_to(DATA) if p.is_relative_to(DATA) else p
        if not p.is_file():
            problems.append(f"MISSING   {label}  ({listing.relative_to(DATA)})")
        elif sha256(p) != digest:
            problems.append(f"MISMATCH  {label}  ({listing.relative_to(DATA)})")
        else:
            ok += 1
    return ok, problems


def verify() -> int:
    """Verify SHA256SUMS and every sidecar; print a summary; return 0 or 1."""
    if not SUMS.is_file():
        print("MISSING   data/SHA256SUMS")
        return 1
    ok, problems = _check_list(SUMS, DATA)
    sidecars = sorted(DATA.rglob("*.sha256"))
    for s in sidecars:
        k, p = _check_list(s, s.parent)
        ok += k
        problems += p
    # An archive directory must hold exactly its listed members (the spec and
    # rule counts are computed by listing the directory).
    for s in sidecars:
        d = s.with_suffix("")
        if d.is_dir():
            listed = {line.split(None, 1)[1].strip() for line in s.read_text().splitlines()
                      if line.strip()}
            for extra in sorted(f"{d.name}/{p.name}" for p in d.iterdir()):
                if extra not in listed:
                    problems.append(f"UNLISTED  {d.parent.relative_to(DATA) / extra}")
    for line in problems:
        print(line)
    print(f"verified {ok} checksums ({len(sidecars)} sidecars + SHA256SUMS); "
          f"{len(problems)} problem(s)")
    return 1 if problems else 0


def clean() -> int:
    """Delete every file restored from a zip, and the two archive directories."""
    removed, dirs = 0, set()
    for z in zips():
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                target = _target(z, name)
                if target.suffix in (".zip", ".sha256") or target == SUMS:
                    continue  # never delete what is committed
                if target.parent != z.parent:
                    dirs.add(target.parent)
                if target.is_file():
                    target.unlink()
                    removed += 1
    for d in sorted(dirs):
        if d.is_dir() and not any(p.suffix in (".zip", ".sha256") for p in d.rglob("*")):
            shutil.rmtree(d)
    print(f"removed {removed} restored file(s) and {len(dirs)} archive directory(ies)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--verify-only", action="store_true", help="verify without extracting")
    group.add_argument("--clean", action="store_true", help="delete the restored files")
    args = ap.parse_args(argv)
    if args.clean:
        return clean()
    if not args.verify_only:
        print(f"extracted {extract()} file(s) from {len(zips())} zip(s)")
    return verify()


if __name__ == "__main__":
    sys.exit(main())
