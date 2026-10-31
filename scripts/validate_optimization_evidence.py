#!/usr/bin/env python3
"""Validate Bitrix optimization audit evidence packs.

The validator checks structure, finding verdicts, referenced evidence files and obvious
secret leaks. It does not execute Bitrix code or claim runtime/perfmon pass.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from evidence_safety import scan_evidence, read_evidence_text, local_evidence_path, field_values


VALID_VERDICTS = {"candidate", "confirmed", "blocked", "fixed", "accepted-risk"}
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
VALID_LAYERS = {
    "component-cache",
    "tagged-cache",
    "managed-cache",
    "cache-invalidation",
    "composite",
    "composite-personalization",
    "db-orm",
    "sql-n-plus-one",
    "frontend-assets",
    "images-assets",
    "agents-imports",
    "shop",
    "shop-side-effects",
    "search-facet-seo",
    "other",
}
REQUIRED_SUMMARY_SECTIONS = [
    "## Scope",
    "## Static audit",
    "## Findings",
    "## Runtime/perfmon",
    "## Safe wins",
    "## Blocked/runtime-needed",
]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class FindingRow:
    finding_id: str
    priority: str
    layer: str
    verdict: str
    evidence_file: str


def read_text(path: Path) -> str:
    return read_evidence_text(path, path.parent)


def add(checks: list[Check], name: str, ok: bool, detail: str = "") -> None:
    checks.append(Check(name, ok, detail))


def find_summary(evidence_dir: Path) -> Path | None:
    candidates = [evidence_dir / "summary.md", evidence_dir / "optimization-summary.md"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    matches = sorted(path for path in evidence_dir.glob("*summary*.md") if path.is_file())
    return matches[0] if matches else None


def parse_finding_rows(summary_text: str) -> list[FindingRow]:
    rows: list[FindingRow] = []
    for line in summary_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        finding_id, priority, layer, verdict, evidence_file = cells[:5]
        if not re.fullmatch(r"OPT-\d{3}", finding_id):
            continue
        rows.append(
            FindingRow(
                finding_id=finding_id.upper(),
                priority=priority.upper(),
                layer=layer.lower(),
                verdict=verdict.lower(),
                evidence_file=evidence_file,
            )
        )
    return rows


def referenced_file_exists(evidence_dir: Path, rel_path: str) -> bool:
    return local_evidence_path(evidence_dir, rel_path) is not None


def validate_finding_files(evidence_dir: Path, rows: list[FindingRow], checks: list[Check]) -> None:
    missing_files = [row.evidence_file for row in rows if not referenced_file_exists(evidence_dir, row.evidence_file)]
    add(
        checks,
        "finding evidence files",
        not missing_files,
        "missing: " + ", ".join(missing_files[:10]) if missing_files else "ok",
    )

    missing_tokens: list[str] = []
    for row in rows:
        if not referenced_file_exists(evidence_dir, row.evidence_file):
            continue
        text = read_text(evidence_dir / row.evidence_file)
        for label, expected in [("ID", row.finding_id), ("Priority", row.priority), ("Layer", row.layer), ("Verdict", row.verdict)]:
            if field_values(text, label) != [expected]:
                missing_tokens.append(f"{row.finding_id}: inconsistent {label}")
        if row.verdict in {"confirmed", "fixed"}:
            references = field_values(text, "Runtime evidence")
            proof = local_evidence_path(evidence_dir, references[0]) if len(references) == 1 else None
            if (proof is None or proof.resolve() == (evidence_dir / row.evidence_file).resolve()
                    or not read_evidence_text(proof, evidence_dir).strip()
                    or field_values(text, "Status") != ["pass"]):
                missing_tokens.append(f"{row.finding_id}: missing runtime evidence or verification pass")
        for token in [row.finding_id, "## Evidence", "## Impact", "## Fix plan", "## Verification"]:
            if token not in text:
                missing_tokens.append(f"{row.evidence_file}: {token}")
    add(
        checks,
        "finding file sections",
        not missing_tokens,
        "; ".join(missing_tokens[:10]) if missing_tokens else "ok",
    )


def validate_forbidden_secrets(evidence_dir: Path, checks: list[Check]) -> None:
    problems = scan_evidence(evidence_dir)
    add(checks, "obvious secret scan", not problems, "; ".join(problems[:10]) if problems else "ok")


def validate_evidence(evidence_dir: Path) -> list[Check]:
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
    missing_sections = [section for section in REQUIRED_SUMMARY_SECTIONS if section not in summary_text]
    add(checks, "summary sections", not missing_sections, "missing: " + ", ".join(missing_sections) if missing_sections else "ok")

    rows = parse_finding_rows(summary_text)
    add(checks, "finding rows", bool(rows), f"{len(rows)} finding row(s)")
    add(checks, "unique finding ids", len({row.finding_id for row in rows}) == len(rows), "one row per finding ID")

    invalid_priority = [row.finding_id for row in rows if row.priority not in VALID_PRIORITIES]
    add(checks, "finding priorities", not invalid_priority, "invalid: " + ", ".join(invalid_priority) if invalid_priority else "ok")

    invalid_layer = [f"{row.finding_id}:{row.layer}" for row in rows if row.layer not in VALID_LAYERS]
    add(checks, "finding layers", not invalid_layer, "invalid: " + ", ".join(invalid_layer[:10]) if invalid_layer else "ok")

    invalid_verdict = [f"{row.finding_id}:{row.verdict}" for row in rows if row.verdict not in VALID_VERDICTS]
    add(checks, "finding verdicts", not invalid_verdict, "invalid: " + ", ".join(invalid_verdict[:10]) if invalid_verdict else "ok")

    validate_finding_files(evidence_dir, rows, checks)

    runtime_needed = [row.finding_id for row in rows if row.verdict in {"candidate", "blocked"}]
    has_runtime_section = "## Blocked/runtime-needed" in summary_text and "## Runtime/perfmon" in summary_text
    add(
        checks,
        "runtime-needed explicitly tracked",
        not runtime_needed or has_runtime_section,
        ", ".join(runtime_needed[:10]) if runtime_needed and not has_runtime_section else "ok",
    )

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Bitrix optimization audit evidence pack")
    parser.add_argument("evidence_dir", type=Path, help="Path to optimization evidence directory")
    args = parser.parse_args()

    checks = validate_evidence(args.evidence_dir)
    width = max(len(check.name) for check in checks)
    failed = [check for check in checks if not check.ok]
    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        print(f"{status}  {check.name:<{width}}  {check.detail}")

    if failed:
        print(f"\nFAILED: {len(failed)} check(s)")
        return 1
    print("\nOptimization evidence validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
