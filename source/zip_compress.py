#!/usr/bin/env python3
"""Rename the newest dist folder to claude-code-package and create a zip archive."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

BASE_DIR = Path("dist/gaic-dev-ap-northeast-1")
TARGET_NAME = "claude-code-package"
TARGET_ZIP = f"{TARGET_NAME}.zip"


def _folder_timestamp(path: Path) -> float:
    """Return creation time if available, otherwise modification time."""
    stat = path.stat()
    birthtime = getattr(stat, "st_birthtime", None)
    if birthtime is not None:
        return float(birthtime)
    return float(stat.st_mtime)


def main() -> int:
    try:
        base_dir = BASE_DIR.resolve()

        if not base_dir.exists():
            raise FileNotFoundError(f"Base directory does not exist: {base_dir}")
        if not base_dir.is_dir():
            raise NotADirectoryError(f"Base path is not a directory: {base_dir}")

        target_dir = base_dir / TARGET_NAME
        target_zip = base_dir / TARGET_ZIP

        if target_dir.exists():
            raise FileExistsError(f"Target directory already exists: {target_dir}")
        if target_zip.exists():
            raise FileExistsError(f"Target zip already exists: {target_zip}")

        candidates = [
            entry
            for entry in base_dir.iterdir()
            if entry.is_dir() and entry.name != TARGET_NAME
        ]

        if not candidates:
            raise FileNotFoundError(f"No candidate directories found in: {base_dir}")

        newest_dir = max(candidates, key=_folder_timestamp)
        renamed_dir = newest_dir.rename(target_dir)

        zip_base = base_dir / TARGET_NAME
        archive_path = shutil.make_archive(
            base_name=str(zip_base),
            format="zip",
            root_dir=str(base_dir),
            base_dir=TARGET_NAME,
        )

        print(f"Renamed: {newest_dir} -> {renamed_dir}")
        print(f"Created zip: {archive_path}")
        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
