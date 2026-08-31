# Decision log discipline

Write a `DECISION-LOG.md` entry for any decision that isn't obviously reversible or obviously trivial:
picking a dependency, a data format, a scoring methodology, a scope boundary, anything where a future
session (or a future you) might otherwise re-litigate the choice.

Use the fixed template in `DECISION-LOG.md`. The two fields that matter most:

- **Trade-offs (what I deliberately did NOT do):** This is what stops the same decision from being
  re-opened a month later for no new reason. Write down the alternative you rejected and why, even in
  one line.
- **Rule Updated:** The load-bearing field. Ask: did this decision reveal a pattern that will recur? If
  yes, update the relevant rule file (`.claude/rules/*.md`) right now, in the same turn — don't defer it.
  If it's not clearly a pattern yet but might be, write `N — flag for retro` so `/retro` can catch it if
  it recurs.

Never edit a past entry. If a decision gets reversed or superseded, append a new entry and set the old
one's **Status** to `Superseded by YYYY-MM-DD entry`.

## Retrospective

Run `/retro` periodically (weekly-ish, or whenever the log feels like it's accumulating similar entries).
It reads recent `DECISION-LOG.md` entries, finds anything with the same underlying pattern occurring 3+
times, and proposes a new or updated rule file. Without this step the log is just a journal; with it, the
rule files (and therefore CLAUDE.md's routing) get sharper over time.
