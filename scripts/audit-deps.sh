#!/usr/bin/env bash
# Run pip-audit and pip-licenses against the locked runtime dependencies.
#
# The script always exits 0. Findings are written to JSON files for the
# caller to render or gate on. The typical renderer is
# scripts/render-audit.py. Inputs are pyproject.toml and uv.lock, read by
# `uv export`.
#
# Outputs in $PWD:
#   requirements-audit.txt  exported runtime requirements with hashes
#   audit.json              pip-audit JSON output (vulnerabilities)
#   licenses.json           pip-licenses JSON output

set -euo pipefail

# Export runtime + extras (no dev), with hashes for pip-audit verification.
uv export \
    --format requirements-txt \
    --no-dev \
    --no-emit-project \
    --all-extras \
    -o requirements-audit.txt

# Vulnerability scan. --disable-pip is required when running under uv-managed
# Python, which ships without pip.
uv run pip-audit \
    -r requirements-audit.txt \
    --require-hashes \
    --disable-pip \
    --format=json \
    -o audit.json || true

# License scan. Package definition lines start in column 0; hash continuations
# and `# via` comments are indented, so a column-anchored grep extracts the
# names cleanly.
PACKAGES=$(grep -oE '^[A-Za-z0-9][A-Za-z0-9._-]*' requirements-audit.txt | sort -u | xargs)
uv run pip-licenses \
    --from=mixed \
    --packages $PACKAGES \
    --format=json > licenses.json || true
