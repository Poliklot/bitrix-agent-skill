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

from evidence_safety import scan_evidence, read_evidence_text, local_evidence_path, field_values


VALID_VERDICTS = {"pass", "fail", "blocked"}
REQUIRED_SCENARIOS = {
    "P1": [f"P1-{index:02d}" for index in range(1, 9)],
    "P2": [f"P2-{index:02d}" for index in range(1, 9)],
    "P3": [f"P3-{index:02d}" for index in range(1, 8)],
    "P4": [f"P4-{index:02d}" for index in range(1, 9)],
}
CORE_MODULES = ["main", "iblock", "catalog", "currency", "sale"]



@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


def read_text(path: Path) -> str:
    return read_evidence_text(path, path.parent)


def add(checks: list[Check], name: str, ok: bool, detail: str = "") -> None:
    checks.append(Check(name, ok, detail))


def find_summary(evidence_dir: Path) -> Path | None:
    candidates = [evidence_dir / "summary.md", evidence_dir / "evidence-summary.md"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    matches = sorted(path for path in evidence_dir.glob("*summary*.md") if path.is_file())
    return matches[0] if matches else None


@dataclass
class ScenarioRow:
    scenario: str
    verdict: str
    evidence_file: str


def parse_scenario_rows(summary_text: str) -> list[ScenarioRow]:
    rows = []
    for line in summary_text.splitlines():
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and len(cells) >= 3 and re.fullmatch(r"P\d+-\d+", cells[0], re.I):
            rows.append(ScenarioRow(cells[0].upper(), cells[1].lower(), cells[2]))
    return rows


def validate_scenario_file(root: Path, row: ScenarioRow) -> bool:
    path = local_evidence_path(root, row.evidence_file)
    if path is None:
        return False
    text = read_evidence_text(path, root)
    if field_values(text, "ID сценария|Scenario") != [row.scenario]:
        return False
    if field_values(text, "Verdict") != [row.verdict]:
        return False
    if row.verdict in {"fail", "blocked"}:
        reasons = field_values(text, "Причина[^:\n]*|Reason")
        return len(reasons) == 1 and reasons[0] not in {"", "-", "—", "n/a"}
    # A verdict alone is not an evidence record. This remains a structure check.
    return bool(re.search(r"^## Evidence\s*\n+(?!#)(?:[^\n]*\S[^\n]*)", text, re.M))


def infer_packages(verdicts: dict[str, str], requested: list[str]) -> list[str]:
    if requested:
        return requested
    packages = sorted({scenario.split("-", 1)[0] for scenario in verdicts})
    return packages or ["P1"]


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
    problems = scan_evidence(evidence_dir)
    add(checks, "obvious secret scan", not problems, "; ".join(problems[:10]) if problems else "ok")


def validate_evidence(evidence_dir: Path, packages: list[str]) -> list[Check]:
    checks: list[Check] = []
    add(checks, "evidence dir exists", evidence_dir.is_dir(), str(evidence_dir))
    if not evidence_dir.is_dir():
        return checks

    validate_forbidden_secrets(evidence_dir, checks)
    if not checks[-1].ok:
        return checks

    summary = find_summary(evidence_dir)
    add(checks, "summary file", summary is not None, str(summary.relative_to(evidence_dir)) if summary else "missing summary.md")
    if summary is None:
        return checks

    summary_text = read_text(summary)
    validate_modules(summary_text, checks)

    rows = parse_scenario_rows(summary_text)
    verdicts = {row.scenario: row.verdict for row in rows}
    add(checks, "unique scenario ids", len(rows) == len(verdicts), "duplicate scenario rows" if len(rows) != len(verdicts) else "ok")
    known = {scenario for required in REQUIRED_SCENARIOS.values() for scenario in required}
    add(checks, "known scenario ids", all(row.scenario in known for row in rows), "only P1-P4 contract ids are accepted")
    add(checks, "all verdict values", all(row.verdict in VALID_VERDICTS for row in rows), "pass/fail/blocked only")
    invalid_files = [row.scenario for row in rows if not validate_scenario_file(evidence_dir, row)]
    add(checks, "scenario file contracts", not invalid_files, ", ".join(invalid_files) if invalid_files else "ok")
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
