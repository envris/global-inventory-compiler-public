#!/usr/bin/env bash
# Post or update a sticky comment on the current pull request via the
# GitHub REST API. An existing comment is identified by an HTML comment
# marker on its first line. If no comment carries the marker, a new one
# is created.
#
# Required environment:
#   GH_TOKEN              token with pull-requests:write
#   GITHUB_REPOSITORY     owner/name (set automatically in GitHub Actions)
#   PR_NUMBER             pull request number to comment on
#
# Arguments:
#   $1  marker string (e.g., "<!-- ci/audit -->")
#   $2  path to file containing the comment body (markdown)

set -euo pipefail

MARKER="$1"
BODY_FILE="$2"

# Prepend the marker so the comment is identifiable on subsequent runs.
{
    echo "$MARKER"
    cat "$BODY_FILE"
} > _comment-body.md

EXISTING=$(gh api --paginate \
    "repos/$GITHUB_REPOSITORY/issues/$PR_NUMBER/comments" \
    --jq ".[] | select(.body | startswith(\"$MARKER\")) | .id" \
    | head -1)

if [ -n "$EXISTING" ]; then
    gh api "repos/$GITHUB_REPOSITORY/issues/comments/$EXISTING" \
        --method PATCH \
        -f body=@_comment-body.md > /dev/null
    echo "Updated existing comment ${EXISTING}."
else
    gh api "repos/$GITHUB_REPOSITORY/issues/$PR_NUMBER/comments" \
        --method POST \
        -f body=@_comment-body.md > /dev/null
    echo "Posted new comment."
fi

rm -f _comment-body.md
