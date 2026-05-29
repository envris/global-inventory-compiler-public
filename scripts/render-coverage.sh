#!/usr/bin/env bash
# Render coverage results to a markdown summary. The script reads the
# .coverage data file produced by `pytest --cov` and writes a markdown
# document containing the overall total and a collapsible table of per
# module coverage.
#
# Arguments:
#   $1  output path (markdown)

set -euo pipefail

OUTPUT="$1"

TOTAL=$(uv run coverage report --format=total)

{
    echo "## Coverage"
    echo
    echo "**Total: ${TOTAL}%**"
    echo
    echo "<details>"
    echo "<summary>Per-module coverage</summary>"
    echo
    uv run coverage report --format=markdown
    echo
    echo "</details>"
} > "$OUTPUT"
