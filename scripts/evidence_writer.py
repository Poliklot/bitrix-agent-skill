"""Write rendered evidence packs after collision checks; serialize cooperating writers."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


def validate_filename(value: str) -> str:
    if not value or value in {".", ".."} or any(char in value for char in "/\\:\r\n\x00"):
        raise ValueError("static report must be a non-empty filename")
    return value


def write_pack(output: Path, files: dict[str, str], force: bool, preserve: set[str] | None = None) -> None:
    preserve = preserve or set()
    if output.is_symlink():
        raise ValueError("output directory must not be a symlink")
    output.mkdir(parents=True, exist_ok=True)
    root = output.resolve()
    lock = root / ".evidence-init.lock"
    # Exclusive creation: never delete a lock belonging to another invocation.
    with lock.open("x", encoding="utf-8"):
        pass
    try:
        pending: list[tuple[Path, str]] = []
        for name, text in files.items():
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("output file must stay inside the evidence pack")
            target = root / relative
            current = root
            for part in relative.parts:
                current = current / part
                if current.is_symlink():
                    raise ValueError("evidence destination must not contain symlinks")
                if current != target and current.exists() and not current.is_dir():
                    raise ValueError("evidence parent is not a directory")
            if target.exists():
                if not target.is_file():
                    raise ValueError("evidence destination is not a regular file")
                if name in preserve:
                    continue
                if not force:
                    raise FileExistsError(f"file exists: {name}; use --force to overwrite")
            pending.append((target, text))
        for target, text in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            if not force:
                # Unlike exists()+write_text(), this cannot overwrite a concurrent file.
                with target.open("x", encoding="utf-8") as stream:
                    stream.write(text)
            else:
                descriptor, temp_name = tempfile.mkstemp(prefix=".evidence-", dir=target.parent)
                try:
                    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                        stream.write(text)
                    os.replace(temp_name, target)
                finally:
                    Path(temp_name).unlink(missing_ok=True)
    finally:
        lock.unlink()
