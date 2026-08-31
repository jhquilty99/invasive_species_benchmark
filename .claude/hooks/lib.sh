#!/usr/bin/env bash
# Shared helpers for hooks. Sourced, not executed directly.
#
# Deliberately pure-bash/grep, no jq or python3 dependency: on this machine `python3`/`python`
# resolve to Windows Store stub aliases that fail at runtime despite `command -v` succeeding,
# and jq isn't installed. A hook that silently fails to parse JSON fails OPEN (e.g. the secret
# guard would let everything through), which is worse than a slightly cruder extraction method.

# json_get <json-string> <dotted.path> -> prints the value of the path's LAST segment (leaf key).
# Handles string, bool, and bare-token (null/number) values. Not a real JSON parser — sufficient
# for the flat, known-shape payloads Claude Code hooks receive.
json_get() {
  local json="$1" path="$2" key="${2##*.}"
  # String value: "key":"value" (value has no unescaped double quotes in our inputs)
  local val
  val="$(printf '%s' "$json" | grep -oP "\"${key}\"\s*:\s*\"\K[^\"]*" | head -n1)"
  if [ -n "$val" ]; then
    printf '%s' "$val"
    return
  fi
  # Bare value: "key":true / "key":false / "key":123
  val="$(printf '%s' "$json" | grep -oP "\"${key}\"\s*:\s*\K(true|false|[0-9]+)" | head -n1)"
  printf '%s' "$val"
}

# json_escape <string> -> prints the string with JSON-unsafe characters escaped, for embedding
# inside a hand-built JSON string value.
json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\t'/\\t}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\n'/\\n}"
  printf '%s' "$s"
}
