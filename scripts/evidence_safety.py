"""Shared fail-closed checks for text evidence; never echo matched secret values."""
from __future__ import annotations

import os
import re
from pathlib import Path

from local_files import is_local_file

MAX_EVIDENCE_SIZE = 2_000_000

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:password|passwd|secret|token|cookie|sessid|php_sessid|phpsessid)\b\s*[:=]\s*[^\s`'\"]{8,}"),
    re.compile(r"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)\bBX_USER_ID\s*[:=]\s*[^\s`'\"]{8,}"),
    re.compile(r"(?i)\b(?:access_token|refresh_token|client_secret|application_token)\b\s*[:=]\s*[^\s`'\"]{8,}"),
    re.compile(r"(?i)\b(?:BITRIX_SM_LOGIN|BITRIX_SM_UIDH|PHPSESSID|BX_USER_ID)\b\s*[:=]\s*[^\s`'\"]{8,}"),
    re.compile(r"(?i)\b(?:DBPassword|DBLogin|DBName)\b\s*=\s*['\"][^'\"]{4,}['\"]"),
    re.compile(r"(?i)['\"](?:password|passwd|secret|token|license_key)['\"]\s*=>\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"(?i)['\"](?:password|passwd|secret|token|license_key)['\"]\s*=>\s*array\s*\([^)]*['\"]value['\"]\s*=>\s*['\"][^'\"]{8,}['\"]", re.DOTALL),
    re.compile(r"(?i)\b(?:BITRIX_LICENSE_KEY|LICENSE_KEY|BX_LICENSE_KEY)\b\s*[:=]\s*[^\s`'\"]{8,}"),
    re.compile(r"https?://[^\s`'\"]+/rest/\d+/[A-Za-z0-9._~+=-]{8,}/"),
]
SECRET_PATTERNS.extend([
    re.compile(r"(?i)[\"'](?:password|passwd|secret|token|access_token|refresh_token|client_secret|application_token|cookie|sessid|license_key)[\"']\s*(?::|=>|=)\s*[\"'](?!<redacted>[\"']|REDACTED[\"'])[^\"'\r\n]+[\"']"),
    re.compile(r"(?i)\bAuthorization\s*:\s*Basic\s+[A-Za-z0-9+/=]+"),
    re.compile(r"https?://[^\s/]+:[^\s/]+@"),
])


def read_evidence_text(path: Path, root: Path) -> str:
    if not is_local_file(path, root):
        raise ValueError("not a regular local evidence file")
    with path.open("rb") as stream:
        data = stream.read(MAX_EVIDENCE_SIZE + 1)
    if len(data) > MAX_EVIDENCE_SIZE:
        raise ValueError("evidence file exceeds scan limit")
    if b"\x00" in data:
        raise ValueError("binary evidence requires a separate review")
    return data.decode("utf-8", errors="strict")


def scan_evidence(root: Path) -> list[str]:
    problems: list[str] = []
    def walk_error(_error: OSError) -> None:
        problems.append("unreadable evidence directory")
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        parent = Path(directory)
        for name in list(dirs):
            if (parent / name).is_symlink():
                problems.append(f"{(parent / name).relative_to(root)}: symlink not scanned")
                dirs.remove(name)
        for name in sorted(files):
            path = parent / name
            label = str(path.relative_to(root))
            try:
                text = read_evidence_text(path, root)
            except (OSError, ValueError, RuntimeError):
                problems.append(f"{label}: unreadable, non-text, oversized or linked evidence")
                continue
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                problems.append(f"{label}: possible secret")
    return problems


def local_evidence_path(root: Path, reference: str) -> Path | None:
    """Only relative, regular files inside this pack can serve as evidence."""
    path = Path(reference)
    if not reference or path.is_absolute() or ".." in path.parts or ":" in reference or "\\" in reference:
        return None
    target = root / path
    return target if is_local_file(target, root) else None


def field_values(text: str, label: str) -> list[str]:
    return [match.strip().strip("`") for match in re.findall(
        rf"^\s*-?\s*(?:{label}):[ \t]*([^\r\n]*)$", text, flags=re.MULTILINE | re.IGNORECASE
    )]
