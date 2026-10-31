"""Bounded, non-symlink filesystem traversal for read-only diagnostics."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator


def is_local_file(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
        current = root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                return False
        path.resolve().relative_to(root.resolve())
        return path.is_file()
    except (OSError, ValueError, RuntimeError):
        return False


def iter_local_files(root: Path, excluded: set[str]) -> Iterator[Path]:
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        dirs[:] = sorted(name for name in dirs if name not in excluded and not (parent / name).is_symlink())
        for name in sorted(files):
            path = parent / name
            if name not in excluded and is_local_file(path, root):
                yield path
