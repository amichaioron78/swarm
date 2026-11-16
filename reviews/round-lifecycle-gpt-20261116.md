# Round lifecycle independent review — 16 November 2026

Reviewed exact head: `d71853f499b8d70704232187eae9e81e1ed3d8e6`
on `claude/round-lifecycle`, against main `b7620ac`.

Verdict: approve the bounded in-memory lifecycle core for the proof of concept,
with the reporting caveat below. This is a review artifact, not a merge or an
owner vote. No production-readiness or provider-metering claim.

## Verified

- Spent commitments never become spendable in a later round. Returning unspent
  units to the room is consistent with the existing committed-pool model and
  gives task #3 a usable round ID; it does not create new provider capacity.
- Four additional tests exercise 100 rounds over contributions 1/3/7/100,
  conservation after each debit and closure, exhaustion, invalid-operation
  atomicity, detached history, cooldown/rejoin with a team change, and historical
  points after that change. All pass.
- Existing 20 lifecycle/domain tests pass unchanged. Combined 24 pass on Linux
  Python 3.12.14 and `/usr/bin/python3` 3.13.5. Node simulator: 14/14 pass.
- No Mac execution or Python 3.9 run was possible. These Linux runs do not
  satisfy the repository's Mac two-interpreter check.

## Follow-up: historical scoreboard mixes scopes

`scoreboard(1)` filters scores to round 1, but `remaining_work_units`,
`spent_work_units`, and `round_id` still describe the current room. Example:
spend 10 in round 1, close it, start round 2 and spend 7. `round_summary(1)`
correctly says spent=10, whereas `scoreboard(1)` says spent_work_units=17 and
round_id=2. Its docstring promises only filtered team totals, so this is not a
conservation failure. Before a UI or ledger consumes this API, name these fields
as room-wide or return round-specific metrics from the existing snapshot. Keep
the default cumulative API compatible and test both scopes.

## Existing limitations retained

Task #3 still needs owner/worker attribution, debit operation IDs and referee
attribution. Empty-team policy (#4), departed-contributor eligibility (#5),
locked rubrics (#7), and real authorization remain unresolved. The current
model can credit an inactive member absent from a new round's membership
snapshot: do not treat snapshot creation as resolving #5. Historical 30%
capacity/fixed-referee wording is not current owner policy; the owner's 10%
target and optional competition/reviewer-role direction take precedence.

## PR #1 findings independently verified

Reviewed current `poc/github-workspace` head
`3134c51f583d8cf015bfbfe23b34d5c9fb5efb72`, matching Claude's review at
`8bf5e8b548c8cd4a3f5aa84b59c0ab71f43c23cd`.

1. In a temporary root, write `workspace/records/broken.json` containing
   `{"schema_version":1,"title":"x"}`. `skills` exits 1 with
   `KeyError: 'kind'`; `show unknown-id` exits 1 with `KeyError: 'id'`.
   Both read commands should remain usable with validation warnings.
2. Copy the fixture's approved review, change its ID and status to
   `changes_requested`, and prepend it before the original approval by the same
   author on the same digest. Validation still reports an unresolved blocking
   review. The schema has no explicit supersession relation or ordering rule;
   list order alone cannot resolve it. Add explicit supersession with same
   reviewer/target/digest checks and reject cycles/ambiguous histories; preserve
   old records rather than deleting a blocker.

PR #1's 25 existing workspace tests still pass. This confirms missing regression
coverage, not absence of those defects. Both fixes are queued; PR #1 remains
unmerged. Minor findings in Claude's report were not independently reproduced
in this bounded review.

## Next task

Fix PR #1 malformed-record reads and explicit review supersession, with failure
tests. Claude can address the scoreboard scope caveat on its own branch. Keep
task #3 isolated until its integration base is agreed. No font review request
was sent in this session.
