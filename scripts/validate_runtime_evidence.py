#!/usr/bin/env python3
"""Validate Bitrix runtime smoke evidence packs.

The validator checks structure, scenario verdicts, core module rows, scenario files,
and obvious secret leaks. It does not execute Bitrix smoke tests and does not inspect
production systems.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


VALID_VERDICTS = {"pass", "fail", "blocked"}
REQUIRED_SCENARIOS = {
    "P1": [f"P1-{index:02d}" for index in range(1, 9)],
    "P2": [f"P2-{index:02d}" for index in range(1, 9)],
    "P3": [f"P3-{index:02d}" for index in range(1, 8)],
    "P4": [f"P4-{index:02d}" for index in range(1, 9)],
}
CORE_MODULES = ["main", "iblock", "catalog", "currency", "sale"]
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:password|passwd|secret|token|cookie|sessid|php_sessid|phpsessid)\b\s*[:=]\s*[^\s`'\"]{8,}"),
    re.compile(r"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)\bBX_USER_ID\s*[:=]\s*[^\s`'\"]{8,}"),
]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def add(checks: list[Check], name: str, ok: bool, detail: str = "") -> None:
    checks.append(Check(name, ok, detail))


def find_summary(evidence_dir: Path) -> Path | None:
    candidates = [evidence_dir / "summary.md", evidence_dir / "evidence-summary.md"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    matches = sorted(evidence_dir.glob("*summary*.md"))
    return matches[0] if matches else None


def extract_verdicts(summary_text: str) -> dict[str, str]:
    verdicts: dict[str, str] = {}
    # Markdown table rows such as: | P1-01 | pass | P1-01-modules.txt | notes |
    for scenario, verdict in re.findall(r"\|\s*(P\d-\d{2})\s*\|\s*(pass|fail|blocked)\s*\|", summary_text, flags=re.IGNORECASE):
        verdicts[scenario.upper()] = verdict.lower()
    # Fallback free-form lines: Scenario: P1-01 ... Verdict: pass
    for block in re.split(r"(?=Scenario\s*:\s*P\d-\d{2})", summary_text, flags=re.IGNORECASE):
        scenario_match = re.search(r"Scenario\s*:\s*(P\d-\d{2})", block, flags=re.IGNORECASE)
        verdict_match = re.search(r"Verdict\s*:\s*(pass|fail|blocked)", block, flags=re.IGNORECASE)
        if scenario_match and verdict_match:
            verdicts[scenario_match.group(1).upper()] = verdict_match.group(1).lower()
    return verdicts


def infer_packages(verdicts: dict[str, str], requested: list[str]) -> list[str]:
    if requested:
        return requested
    packages = sorted({scenario.split("-", 1)[0] for scenario in verdicts})
    return packages or ["P1"]


def scenario_file_exists(evidence_dir: Path, scenario: str) -> bool:
    patterns = [
        f"{scenario}*",
        f"{scenario.lower()}*",
    ]
    for pattern in patterns:
        for path in evidence_dir.glob(pattern):
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".log", ".html"}:
                return True
    return False


def validate_modules(summary_text: str, checks: list[Check]) -> None:
    missing_rows = []
    for module in CORE_MODULES:
        if not re.search(rf"\|\s*`?{re.escape(module)}`?\s*\|", summary_text):
            missing_rows.append(module)
    add(
        checks,
        "core module rows",
        not missing_rows,
        "missing: " + ", ".join(missing_rows) if missing_rows else "ok",
    )


def validate_forbidden_secrets(evidence_dir: Path, checks: list[Check]) -> None:
    matches: list[str] = []
    for path in sorted(evidence_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.stat().st_size > 2_000_000:
            continue
        text = read_text(path)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                matches.append(str(path.relative_to(evidence_dir)))
                break
    add(
        checks,
        "obvious secret scan",
        not matches,
        ", ".join(matches[:10]) if matches else "ok",
    )


def validate_evidence(evidence_dir: Path, packages: list[str]) -> list[Check]:
    checks: list[Check] = []
    add(checks, "evidence dir exists", evidence_dir.is_dir(), str(evidence_dir))
    if not evidence_dir.is_dir():
        return checks

    summary = find_summary(evidence_dir)
    add(checks, "summary file", summary is not None, str(summary.relative_to(evidence_dir)) if summary else "missing summary.md")
    if summary is None:
        validate_forbidden_secrets(evidence_dir, checks)
        return checks

    summary_text = read_text(summary)
    validate_modules(summary_text, checks)

    verdicts = extract_verdicts(summary_text)
    add(checks, "scenario verdicts present", bool(verdicts), f"{len(verdicts)} verdict(s)")

    selected_packages = infer_packages(verdicts, packages)
    unknown_packages = [package for package in selected_packages if package not in REQUIRED_SCENARIOS]
    add(checks, "requested packages", not unknown_packages, "unknown: " + ", ".join(unknown_packages) if unknown_packages else ", ".join(selected_packages))

    for package in selected_packages:
        if package not in REQUIRED_SCENARIOS:
            continue
        required = REQUIRED_SCENARIOS[package]
        missing = [scenario for scenario in required if scenario not in verdicts]
        add(
            checks,
            f"{package} required scenarios",
            not missing,
            "missing: " + ", ".join(missing) if missing else "ok",
        )
        invalid = [scenario for scenario in required if verdicts.get(scenario) and verdicts[scenario] not in VALID_VERDICTS]
        add(
            checks,
            f"{package} verdict values",
            not invalid,
            "invalid: " + ", ".join(invalid) if invalid else "ok",
        )
        missing_files = [scenario for scenario in required if scenario in verdicts and not scenario_file_exists(evidence_dir, scenario)]
        add(
            checks,
            f"{package} scenario files",
            not missing_files,
            "missing files: " + ", ".join(missing_files) if missing_files else "ok",
        )

    blocked_or_failed = [scenario for scenario, verdict in verdicts.items() if verdict in {"fail", "blocked"}]
    if blocked_or_failed:
        has_reason_section = bool(re.search(r"(?i)(blocked checks|заблокированные проверки|failed contracts|сломанные контракты|reason)", summary_text))
        add(
            checks,
            "fail/blocked reasons",
            has_reason_section,
            ", ".join(blocked_or_failed) if not has_reason_section else "ok",
        )
    else:
        add(checks, "fail/blocked reasons", True, "no fail/blocked verdicts")

    validate_forbidden_secrets(evidence_dir, checks)
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Bitrix runtime smoke evidence pack")
    parser.add_argument("evidence_dir", type=Path, help="Path to evidence directory")
    parser.add_argument(
        "--package",
        action="append",
        choices=sorted(REQUIRED_SCENARIOS),
        help="Required package to validate. Can be repeated. Defaults to packages found in summary, or P1.",
    )
    args = parser.parse_args()

    packages = [package.upper() for package in (args.package or [])]
    checks = validate_evidence(args.evidence_dir, packages)
    width = max(len(check.name) for check in checks)
    failed = [check for check in checks if not check.ok]
    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        print(f"{status}  {check.name:<{width}}  {check.detail}")

    if failed:
        print(f"\nFAILED: {len(failed)} check(s)")
        return 1
    print("\nRuntime evidence validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
