#!/usr/bin/env bash
# PreToolUse (Write|Edit): refuse writes to secret/signing/config files via a deny-list.
# Fails open (allows the write) if it can't parse input, rather than blocking all writes on a tooling gap.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib.sh"

INPUT="$(cat)"
FILE_PATH="$(json_get "$INPUT" 'tool_input.file_path')"

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Deny-list: secrets, signing keys, credentials, and config files that gate CI/deploy/permissions.
DENY_PATTERNS=(
  '\.env($|\.)'
  '\.pem$'
  '\.key$'
  '\.pfx$'
  '\.p12$'
  'id_rsa'
  'id_ed25519'
  '(^|/)secrets?[./]'
  '(^|/)credentials'
  '\.npmrc$'
  '\.netrc$'
  '(^|/)\.aws/'
  '(^|/)\.ssh/'
  '(^|/)\.claude/settings\.json$'
)

for pattern in "${DENY_PATTERNS[@]}"; do
  if echo "$FILE_PATH" | grep -qE "$pattern"; then
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Refused: '$FILE_PATH' matches the secrets/signing/config deny-list (pattern: $pattern). If this write is intentional, edit the file manually outside Claude Code, or update .claude/hooks/pre-write-secret-guard.sh's DENY_PATTERNS."
  }
}
EOF
    exit 0
  fi
done

exit 0
