---
description: Read recent DECISION-LOG.md entries, find recurring patterns (3+ occurrences), and propose rule updates.
allowed-tools: Read, Grep, Edit
---

Read `DECISION-LOG.md` in full (or since the last retro, if a prior retro entry marks where you left off).

1. Group entries by underlying pattern, not by surface topic — two decisions about "which test fixture to
   use" and "how to structure a scenario file" might both really be about "where does domain data live,"
   for instance.
2. For any pattern that occurs 3 or more times, or that occurs fewer times but each entry marked
   `Rule Updated: N — flag for retro`, propose a concrete rule addition or edit to the relevant file in
   `.claude/rules/`.
3. Present the proposed rule changes to the user before writing them — don't silently rewrite rule files.
4. Once approved, apply the edits and append a `DECISION-LOG.md` entry documenting the retro itself: what
   pattern was found, which rule file changed, and mark it `Rule Updated: Y`.

If nothing has recurred 3+ times and nothing is flagged, say so — don't invent a rule change to have
something to report.
