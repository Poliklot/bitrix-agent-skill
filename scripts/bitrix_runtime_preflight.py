#!/usr/bin/env python3
"""Collect a safe Bitrix sandbox preflight snapshot for runtime smoke evidence.

The script is intentionally read-only: it checks filesystem structure, module
version files and route candidates, but never prints DB passwords, cookies,
tokens or payload bodies.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


DEFAULT_MODULES = [
    "main",
    "iblock",
    "catalog",
    "currency",
    "sale",
    "rest",
    "webservice",
    "statistic",
    "sender",
    "mail",
    "messageservice",
    "subscribe",
    "bizproc",
    "bizprocdesigner",
    "workflow",
    "lists",
    "pull",
]

ROUTE_PATTERNS = [
    re.compile(r"IncludeComponent\s*\("),
    re.compile(r"catalog\.(?:section|element|smart\.filter|import\.1c|export\.1c)"),
    re.compile(r"sale\.(?:basket|order|personal|export\.1c)"),
    re.compile(r"webservice\.(?:sale|statistic)"),
    re.compile(r"/rest/"),
]

SKIP_DIRS = {
    ".git",
    "bitrix/cache",
    "bitrix/managed_cache",
    "bitrix/stack_cache",
    "bitrix/html_pages",
    "upload",
}


def rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def resolve_public_root(raw_path: str) -> tuple[Path, list[str]]:
    notes: list[str] = []
    candidate = Path(raw_path).expanduser().resolve()
    if (candidate / "bitrix" / "modules").is_dir():
        return candidate, notes
    if (candidate / "www" / "bitrix" / "modules").is_dir():
        notes.append(f"public root inferred from {candidate}/www")
        return (candidate / "www").resolve(), notes
    notes.append("public root with bitrix/modules not found")
    return candidate, notes


def read_small_text(path: Path, limit: int = 200_000) -> str:
    if not path.exists() or not path.is_file() or path.stat().st_size > limit:
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def module_version_file(public_root: Path, module: str) -> Path:
    if module == "main":
        fallback = public_root / "bitrix" / "modules" / "main" / "classes" / "general" / "version.php"
        if fallback.exists():
            return fallback
    return public_root / "bitrix" / "modules" / module / "install" / "version.php"


def parse_module_version(text: str) -> str:
    patterns = [
        r"['\"]VERSION['\"]\s*=>\s*['\"]([^'\"]+)['\"]",
        r"\$arModuleVersion\s*\[\s*['\"]VERSION['\"]\s*\]\s*=\s*['\"]([^'\"]+)['\"]",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""


def collect_modules(public_root: Path, modules: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for module in modules:
        path = module_version_file(public_root, module)
        text = read_small_text(path)
        rows.append(
            {
                "module": module,
                "status": "found" if path.exists() else "missing",
                "version": parse_module_version(text) if text else "",
                "version_file": rel(path, public_root) if path.exists() else "",
            }
        )
    return rows


def path_is_skipped(path: Path, public_root: Path) -> bool:
    relative = rel(path, public_root)
    return any(relative == skip or relative.startswith(skip + os.sep) for skip in SKIP_DIRS)


def iter_route_files(public_root: Path) -> list[Path]:
    candidates = [
        public_root / "local",
        public_root / "bitrix" / "templates",
        public_root / "urlrewrite.php",
    ]
    files: list[Path] = []
    for candidate in candidates:
        if candidate.is_file():
            files.append(candidate)
        elif candidate.is_dir():
            for path in candidate.rglob("*.php"):
                if not path_is_skipped(path, public_root):
                    files.append(path)
    return files


def collect_routes(public_root: Path, limit: int = 25) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for path in iter_route_files(public_root):
        text = read_small_text(path, limit=1_000_000)
        if not text:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in ROUTE_PATTERNS):
                matches.append(
                    {
                        "file": rel(path, public_root),
                        "line": str(line_no),
                        "snippet": line.strip()[:180],
                    }
                )
                if len(matches) >= limit:
                    return matches
    return matches


def collect_safety(public_root: Path) -> list[dict[str, str]]:
    checks = [
        ("settings.php", public_root / "bitrix" / ".settings.php", "contains DB/cache settings; do not paste values into evidence"),
        ("dbconn.php", public_root / "bitrix" / "php_interface" / "dbconn.php", "legacy DB constants may contain credentials"),
        (".env", public_root / ".env", "environment file may contain credentials"),
        ("upload/1c_exchange", public_root / "upload" / "1c_exchange", "CommerceML exchange files may contain private catalog/order data"),
    ]
    return [
        {
            "check": name,
            "status": "present" if path.exists() else "absent",
            "path": rel(path, public_root),
            "note": note if path.exists() else "",
        }
        for name, path, note in checks
    ]


def build_report(public_root: Path, base_url: str, modules: list[str]) -> dict[str, object]:
    resolved_root, notes = resolve_public_root(str(public_root))
    exists = (resolved_root / "bitrix" / "modules").is_dir()
    report: dict[str, object] = {
        "public_root": str(resolved_root),
        "base_url": base_url,
        "status": "pass" if exists else "blocked",
        "notes": notes,
        "modules": collect_modules(resolved_root, modules) if exists else [],
        "safety": collect_safety(resolved_root) if exists else [],
        "routes": collect_routes(resolved_root) if exists else [],
    }
    if not exists:
        report["blocked_reason"] = "public root with bitrix/modules not found"
    return report


def print_markdown(report: dict[str, object]) -> None:
    print("# Bitrix runtime smoke preflight")
    print()
    print(f"- Public root: `{report['public_root']}`")
    if report.get("base_url"):
        print(f"- Base URL: `{report['base_url']}`")
    print(f"- Verdict: `{report['status']}`")
    if report.get("blocked_reason"):
        print(f"- Blocker reason: {report['blocked_reason']}")
    notes = report.get("notes") or []
    for note in notes:
        print(f"- Note: {note}")
    print()

    print("## Modules and versions")
    print()
    print("| Module | Status | Version | Version file |")
    print("|---|---|---:|---|")
    for row in report.get("modules", []):
        print(f"| `{row['module']}` | {row['status']} | {row['version']} | `{row['version_file']}` |")
    if not report.get("modules"):
        print("| — | blocked | | |")
    print()

    print("## Safety markers")
    print()
    print("| Check | Status | Path | Note |")
    print("|---|---|---|---|")
    for row in report.get("safety", []):
        print(f"| {row['check']} | {row['status']} | `{row['path']}` | {row['note']} |")
    if not report.get("safety"):
        print("| public root | blocked | | no filesystem checks |")
    print()

    print("## Route candidates")
    print()
    print("| File | Line | Snippet |")
    print("|---|---:|---|")
    for row in report.get("routes", []):
        snippet = row["snippet"].replace("|", "\\|")
        print(f"| `{row['file']}` | {row['line']} | `{snippet}` |")
    if not report.get("routes"):
        print("| — | | no route candidates found or preflight blocked |")


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Bitrix runtime smoke preflight facts")
    parser.add_argument("--public-root", default=os.environ.get("SMOKE_PUBLIC_ROOT", "www"), help="Bitrix public root, default: SMOKE_PUBLIC_ROOT or www")
    parser.add_argument("--base-url", default=os.environ.get("SMOKE_BASE_URL", ""), help="Sandbox base URL, optional")
    parser.add_argument("--module", action="append", dest="modules", help="Module to check; can be repeated")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    args = parser.parse_args()

    modules = args.modules or DEFAULT_MODULES
    report = build_report(Path(args.public_root), args.base_url, modules)
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print_markdown(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
