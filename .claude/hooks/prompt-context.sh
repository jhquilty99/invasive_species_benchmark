#!/usr/bin/env bash
# UserPromptSubmit: attach current branch + working-tree status so there's no
# "what branch am I on" round trip at the start of a turn.
set -uo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

BRANCH="$(git branch --show-current 2>/dev/null || echo '(detached HEAD)')"
STATUS="$(git status --short 2>/dev/null)"

if [ -z "$STATUS" ]; then
  STATUS="(clean)"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

CONTEXT="Git branch: $BRANCH
Working tree:
$STATUS"

ESCAPED="$(json_escape "$CONTEXT")"
printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' "$ESCAPED"
exit 0
