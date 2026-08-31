#!/usr/bin/env bash
# Cross-references git log against SCRATCHPAD.md's open tasks and flags anything that
# looks done-but-still-active, so archive drift gets caught instead of piling up.
# Run automatically at SessionStart, and on demand via the /scratchpad-audit command.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

cd "$(git rev-parse --show-toplevel)"

if [ ! -f "SCRATCHPAD.md" ]; then
  exit 0
fi

# Heuristic: recent commit subjects that look like they closed something (fix/close/done/complete),
# cross-referenced against task lines still present in the active scratchpad.
RECENT_COMMITS="$(git log --oneline -n 30 --pretty=format:'%s' 2>/dev/null | grep -iE '^(fix|close|complete|done|finish)' || true)"

if [ -z "$RECENT_COMMITS" ]; then
  exit 0
fi

FLAGGED=""
NL=$'\n'
while IFS= read -r line; do
  [ -z "$line" ] && continue
  # Pull a few significant words (4+ chars) out of the commit subject and check whether they
  # still appear in an open task line in SCRATCHPAD.md's "Open tasks" section.
  WORDS="$(echo "$line" | grep -oE '[A-Za-z]{4,}' | tr '[:upper:]' '[:lower:]' | sort -u)"
  for w in $WORDS; do
    if grep -iq "$w" SCRATCHPAD.md 2>/dev/null; then
      MATCH_LINE="$(grep -i "$w" SCRATCHPAD.md | head -n1)"
      FLAGGED="${FLAGGED}${NL}- commit \"$line\" looks closed but SCRATCHPAD.md still has: \"$MATCH_LINE\""
      break
    fi
  done
done <<< "$RECENT_COMMITS"

if [ -n "$FLAGGED" ]; then
  MESSAGE="Scratchpad audit: possible overdue archive items (commit looks done, task still active):${FLAGGED}${NL}${NL}If these are actually closed, append a one-line entry to SCRATCHPAD-ARCHIVE.md now and remove the block from SCRATCHPAD.md."
  ESCAPED="$(json_escape "$MESSAGE")"
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$ESCAPED"
fi

exit 0
