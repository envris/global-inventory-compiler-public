#!/usr/bin/env bash
# Maintain the rolling dependency audit tracking issue.
#
# When findings are present, the existing issue body is updated, or a
# new issue is opened. When findings are clean, the existing issue is
# closed with a "no findings" comment if one is open. Only one open
# issue is expected for a given label and title. The first match is the
# one updated or closed.
#
# Required environment:
#   GH_TOKEN              token with issues:write
#   GITHUB_REPOSITORY     owner/name (set automatically in GitHub Actions)
#
# Arguments:
#   $1  issue label
#   $2  issue title (used to disambiguate within the label)
#   $3  path to file containing the issue body (markdown)
#   $4  has-findings flag ("true" or "false")

set -euo pipefail

LABEL="$1"
TITLE="$2"
BODY_FILE="$3"
HAS_FINDINGS="$4"

ISSUE_NUMBER=$(gh issue list \
    --label "$LABEL" \
    --state open \
    --search "in:title \"$TITLE\"" \
    --limit 1 \
    --json number \
    --jq '.[0].number // empty')

if [ "$HAS_FINDINGS" = "true" ]; then
    if [ -n "$ISSUE_NUMBER" ]; then
        echo "Updating existing tracking issue #${ISSUE_NUMBER}."
        gh issue edit "$ISSUE_NUMBER" --body-file "$BODY_FILE"
    else
        echo "Opening new tracking issue."
        gh issue create \
            --title "$TITLE" \
            --body-file "$BODY_FILE" \
            --label "$LABEL"
    fi
else
    if [ -n "$ISSUE_NUMBER" ]; then
        echo "No findings; closing existing tracking issue #${ISSUE_NUMBER}."
        gh issue close "$ISSUE_NUMBER" \
            --comment "Audit run on $(date -u +%Y-%m-%d) found no known vulnerabilities and no disallowed licenses."
    else
        echo "No findings and no open tracking issue. Nothing to do."
    fi
fi
