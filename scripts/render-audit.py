"""Render pip-audit and pip-licenses JSON output as GitHub Flavoured Markdown.

Used by the CI and scheduled audit workflows to surface dependency
findings in PR comments, workflow summaries, and tracking issues. The
script also sets the `has_findings` GitHub Actions output so callers can
branch on whether any finding was reported.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

ALLOWED_LICENSE_TOKENS = {"MIT", "BSD-3-Clause"}


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    text = path.read_text().strip()
    if not text:
        return None
    return json.loads(text)


def render_audit(audit_json: dict | None) -> tuple[str, int]:
    lines = ["## Dependency vulnerability audit", ""]
    if audit_json is None:
        lines.append("_pip-audit produced no output._")
        return "\n".join(lines), 0

    deps = audit_json.get("dependencies", [])
    findings = [(d["name"], d["version"], v) for d in deps for v in d.get("vulns", [])]
    if not findings:
        lines.append("No known vulnerabilities found.")
        return "\n".join(lines), 0

    noun = "vulnerability" if len(findings) == 1 else "vulnerabilities"
    lines.append(f"**{len(findings)} known {noun} found.**")
    lines.append("")
    lines.append("| Package | Version | Advisory | Fix versions |")
    lines.append("| --- | --- | --- | --- |")
    for name, version, vuln in findings:
        advisory = vuln.get("id", "")
        fix_versions = (
            ", ".join(vuln.get("fix_versions") or []) or "_(no fix available)_"
        )
        lines.append(f"| `{name}` | `{version}` | `{advisory}` | {fix_versions} |")
    return "\n".join(lines), len(findings)


def render_licenses(licenses_json: list | None) -> tuple[str, int]:
    lines = ["## Runtime dependency licenses", ""]
    if licenses_json is None:
        lines.append("_pip-licenses produced no output._")
        return "\n".join(lines), 0

    forbidden = []
    for pkg in licenses_json:
        license_field = pkg.get("License", "UNKNOWN")
        if not any(token in license_field for token in ALLOWED_LICENSE_TOKENS):
            forbidden.append(pkg)

    if not forbidden:
        total = len(licenses_json)
        lines.append(
            f"All {total} runtime dependencies are MIT or BSD-3-Clause licensed."
        )
        return "\n".join(lines), 0

    noun = "dependency" if len(forbidden) == 1 else "dependencies"
    lines.append(f"**{len(forbidden)} {noun} with disallowed license.**")
    lines.append("")
    lines.append("| Package | Version | License |")
    lines.append("| --- | --- | --- |")
    for pkg in forbidden:
        name = pkg.get("Name", "")
        version = pkg.get("Version", "")
        license_field = pkg.get("License", "UNKNOWN")
        lines.append(f"| `{name}` | `{version}` | {license_field} |")
    return "\n".join(lines), len(forbidden)


def write_github_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as fh:
            fh.write(f"{name}={value}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=Path("audit.json"))
    parser.add_argument("--licenses", type=Path, default=Path("licenses.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    audit_md, audit_count = render_audit(load_json(args.audit))
    license_md, license_count = render_licenses(load_json(args.licenses))

    body = f"{audit_md}\n\n{license_md}\n"
    args.output.write_text(body, encoding="utf-8")

    has_findings = "true" if (audit_count + license_count) > 0 else "false"
    write_github_output("has_findings", has_findings)


if __name__ == "__main__":
    main()
