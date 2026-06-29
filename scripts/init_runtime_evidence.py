#!/usr/bin/env python3
"""Initialize a Bitrix runtime smoke evidence pack from bundled templates."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "bitrix" / "assets" / "runtime-smoke"

SCENARIOS = {
    "P1": [
        ("P1-01", "modules"),
        ("P1-02", "catalog-list-detail"),
        ("P1-03", "price-stock"),
        ("P1-04", "offer-selection"),
        ("P1-05", "guest-basket"),
        ("P1-06", "auth-basket"),
        ("P1-07", "order-save"),
        ("P1-08", "cache-pass"),
    ],
    "P2": [
        ("P2-01", "checkauth"),
        ("P2-02", "init-settings"),
        ("P2-03", "file-upload"),
        ("P2-04", "catalog-import"),
        ("P2-05", "repeated-import"),
        ("P2-06", "broken-xml-negative"),
        ("P2-07", "order-export"),
        ("P2-08", "non-eligible-order"),
    ],
    "P3": [
        ("P3-01", "method-discovery"),
        ("P3-02", "missing-scope-negative"),
        ("P3-03", "sale-event"),
        ("P3-04", "catalog-event"),
        ("P3-05", "placement"),
        ("P3-06", "webservice-sale"),
        ("P3-07", "webservice-statistic"),
    ],
    "P4": [
        ("P4-01", "sender-segment"),
        ("P4-02", "subscribe-unsubscribe"),
        ("P4-03", "mail-capture"),
        ("P4-04", "sms-stub"),
        ("P4-05", "banner-click"),
        ("P4-06", "conversion-report-statistic"),
        ("P4-07", "bizproc-list-task"),
        ("P4-08", "pull-realtime"),
    ],
}

DEFAULT_SLUG = {
    "P1": "p1-shop-path",
    "P2": "p2-commerceml",
    "P3": "p3-rest-webservice",
    "P4": "p4-marketing-automation",
}


def read_template(name: str) -> str:
    path = TEMPLATE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"missing template: {path}")
    return path.read_text(encoding="utf-8")


def write_file(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"file exists: {path}; use --force to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_summary(package: str, scenarios: list[tuple[str, str]]) -> str:
    template = read_template("evidence-summary.template.md")
    rows = "\n".join(
        f"| {scenario_id} | pass/fail/blocked | {scenario_id}-{slug}.md | |"
        for scenario_id, slug in scenarios
    )
    template = template.replace(
        "- Smoke package: `P1` / `P2` / `P3` / `P4` / mixed",
        f"- Smoke package: `{package}`",
    )
    start = template.find("| P1-01 |")
    if start == -1:
        return template + "\n" + rows + "\n"
    before = template[:start]
    # Keep the table header and replace the sample P1 rows up to the next section.
    after_marker = "\n\n## Findings"
    end = template.find(after_marker, start)
    if end == -1:
        return before + rows + "\n"
    return before + rows + template[end:]


def init_evidence(package: str, output: Path, force: bool) -> None:
    scenarios = SCENARIOS[package]
    output.mkdir(parents=True, exist_ok=True)

    write_file(output / "summary.md", build_summary(package, scenarios), force)
    shutil.copyfile(TEMPLATE_DIR / "sandbox-preflight.template.md", output / "00-preflight.md") if force or not (output / "00-preflight.md").exists() else None

    scenario_template = read_template("scenario-result.template.md")
    for scenario_id, slug in scenarios:
        text = scenario_template.replace("- ID сценария:", f"- ID сценария: {scenario_id}")
        text = text.replace("- Название сценария:", f"- Название сценария: {slug}")
        write_file(output / f"{scenario_id}-{slug}.md", text, force)


def init_all(output: Path, force: bool) -> list[tuple[str, Path]]:
    created: list[tuple[str, Path]] = []
    output.mkdir(parents=True, exist_ok=True)
    for package in sorted(SCENARIOS):
        package_output = output / DEFAULT_SLUG[package]
        init_evidence(package, package_output, force)
        created.append((package, package_output))
    readme_rows = "\n".join(
        f"| {package} | `{path.name}/summary.md` | "
        f"`python3 scripts/validate_runtime_evidence.py {output}/{path.name} --package {package}` |"
        for package, path in created
    )
    write_file(
        output / "README.md",
        "\n".join(
            [
                "# Runtime smoke evidence pack",
                "",
                "Сгенерированный набор шаблонов для `P1–P4`.",
                "Перед коммитом evidence удали secrets, cookies, session ids, production XML/дампы и персональные данные.",
                "",
                "| Package | Summary | Validation command |",
                "|---|---|---|",
                readme_rows,
                "",
            ]
        ),
        force,
    )
    return created


def resolve_default_output(package: str | None, date_value: str, all_packages: bool) -> Path:
    if all_packages:
        return Path("evidence") / f"{date_value}-runtime-smoke-all"
    selected = package or "P1"
    return Path("evidence") / f"{date_value}-{DEFAULT_SLUG[selected]}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize Bitrix runtime smoke evidence pack")
    parser.add_argument("--package", choices=sorted(SCENARIOS), default=None, help="Smoke package to initialize")
    parser.add_argument("--all", action="store_true", help="Initialize all smoke packages P1-P4 under one directory")
    parser.add_argument("--output", type=Path, help="Output evidence directory")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Date prefix for default output directory, YYYY-MM-DD")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    try:
        dt.date.fromisoformat(args.date)
    except ValueError:
        print(f"ERROR: --date must be YYYY-MM-DD, got: {args.date}", file=sys.stderr)
        return 2

    package = (args.package or "P1").upper()
    output = args.output or resolve_default_output(package, args.date, args.all)
    try:
        if args.all:
            created = init_all(output, args.force)
        else:
            init_evidence(package, output, args.force)
            created = [(package, output)]
    except Exception as exc:  # noqa: BLE001 - CLI should report concise error
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.all:
        print(f"Initialized runtime evidence packs: {output}")
    else:
        print(f"Initialized {package} evidence pack: {output}")
    print("Fill summary.md and scenario files, remove secrets, then run:")
    for created_package, created_output in created:
        print(f"  python3 scripts/validate_runtime_evidence.py {created_output} --package {created_package}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
