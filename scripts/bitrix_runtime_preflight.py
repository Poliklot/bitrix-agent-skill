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
from urllib.parse import urlsplit

from local_files import is_local_file, iter_local_files


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
    try:
        if not path.is_file() or path.stat().st_size > limit:
            return ""
        return path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError):
        return ""


def module_id(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*", value):
        raise ValueError("module must be a module identifier, not a path")
    return value


def module_version_file(public_root: Path, module: str) -> Path:
    module_id(module)
    if module == "main":
        fallback = public_root / "bitrix" / "modules" / "main" / "classes" / "general" / "version.php"
        if is_local_file(fallback, public_root):
            return fallback
    return public_root / "bitrix" / "modules" / module / "install" / "version.php"


def parse_module_version(text: str) -> str:
    patterns = [
        r"define\s*\(\s*['\"]SM_VERSION['\"]\s*,\s*['\"]([0-9]+(?:\.[0-9]+)+)['\"]",
        r"\bconst\s+SM_VERSION\s*=\s*['\"]([0-9]+(?:\.[0-9]+)+)['\"]",
        r"['\"]VERSION['\"]\s*=>\s*['\"]([0-9]+(?:\.[0-9]+)+)['\"]",
        r"\$arModuleVersion\s*\[\s*['\"]VERSION['\"]\s*\]\s*=\s*['\"]([0-9]+(?:\.[0-9]+)+)['\"]",
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
        text = read_small_text(path) if is_local_file(path, public_root) else ""
        rows.append(
            {
                "module": module,
                "status": "found" if text else "missing-or-unreadable",
                "registration": "not_checked",
                "version": parse_module_version(text) if text else "",
                "version_file": rel(path, public_root) if path.exists() else "",
            }
        )
    return rows


def iter_route_files(public_root: Path) -> list[Path]:
    excluded = {".git", "upload", "cache", "managed_cache", "stack_cache", "html_pages", "vendor", "node_modules"}
    files: list[Path] = []
    for subtree in [public_root / "local", public_root / "bitrix/templates"]:
        # Check each boundary before entering it; never walk the whole core tree.
        relative = subtree.relative_to(public_root)
        parents = [public_root.joinpath(*relative.parts[:i]) for i in range(1, len(relative.parts) + 1)]
        if any(path.is_symlink() for path in parents):
            continue
        if subtree.is_dir():
            files.extend(path for path in iter_local_files(subtree, excluded) if path.suffix == ".php")
    rewrite = public_root / "urlrewrite.php"
    if is_local_file(rewrite, public_root):
        files.append(rewrite)
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
                        "snippet": "route marker detected; source omitted",
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


def safe_base_url(value: str) -> str:
    """Report only HTTP(S) origin; paths may contain Bitrix webhook credentials."""
    if not value:
        return ""
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("invalid origin")
        host = parsed.hostname
        if not re.fullmatch(r"[A-Za-z0-9.:-]+", host):
            raise ValueError("invalid host")
        host = f"[{host}]" if ":" in host else host
        port = f":{parsed.port}" if parsed.port is not None else ""
        return f"{parsed.scheme}://{host}{port}"
    except ValueError:
        return "[invalid URL omitted]"


def build_report(public_root: Path, base_url: str, modules: list[str]) -> dict[str, object]:
    resolved_root, notes = resolve_public_root(str(public_root))
    exists = (resolved_root / "bitrix" / "modules").is_dir()
    module_rows = collect_modules(resolved_root, list(dict.fromkeys(["main", *modules]))) if exists else []
    main_available = any(row["module"] == "main" and row["version"] for row in module_rows)
    notes.append("Static filesystem inspection only; module registration, PHP, DB, HTTP and sandbox safety are not checked")
    report: dict[str, object] = {
        "public_root": str(resolved_root),
        "base_url": safe_base_url(base_url),
        "status": "candidate" if main_available else "blocked",
        "runtime_status": "not_checked",
        "notes": notes,
        "modules": module_rows,
        "safety": collect_safety(resolved_root) if exists else [],
        "routes": collect_routes(resolved_root) if exists else [],
    }
    if not main_available:
        report["blocked_reason"] = "main version unavailable; filesystem presence does not prove a runnable sandbox"
    return report


def print_markdown(report: dict[str, object]) -> None:
    print("# Bitrix runtime smoke preflight")
    print()
    print(f"- Public root: `{report['public_root']}`")
    if report.get("base_url"):
        print(f"- Base URL: `{report['base_url']}`")
    print(f"- Verdict: `{report['status']}`")
    print(f"- Runtime: `{report['runtime_status']}`")
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
    parser.add_argument("--module", action="append", dest="modules", type=module_id, help="Module to check; can be repeated")
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
