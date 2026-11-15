# Independent review: PR #1 `poc/github-workspace` (Claude, 2026-11-15)

Reviewed head: `3134c51` (3 commits on top of `main` b7620ac). Read-only review; nothing on the PR branch was changed.

## Verdict

**Works as a proof of concept; approve with changes.** The validator, tests and CI layout are sound. Two crash bugs in the read commands and one design gap in the "blocking review" rule should be fixed before the workspace is relied on.

## What I ran (cloud Linux, Python 3.13.18, Node test runner)

- `python3 tools/workspace.py validate` → `Valid: 6 records`
- `python3 -m unittest discover -s tests` → 25 tests OK
- `python3 -m unittest discover -s swarm_mvp` → 12 tests OK
- `npm test` in `swarm_simulator` → 14/14 pass
- Probes on a scratch copy (results below).
- NOT run: the Mac two-Python rule (`/usr/bin/python3` 3.9 and Homebrew 3.13). The CI matrix covers 3.9 and 3.13 but I did not see a CI run.

## Findings

1. **Bug: `skills` and `show` crash on an invalid record** (`tools/workspace.py` lines 216 and 220). They use `r['kind']` / `r['id']`, and `KeyError` is not in the caught exceptions (line 224). The README promises read commands "warn about invalid records but remain usable". Reproduced: adding `{"schema_version":1,"title":"x"}` as a record → `skills` exits with a `KeyError: 'kind'` traceback; `show <unknown-id>` exits with `KeyError: 'id'`. Fix: use `r.get(...)` in both places (and add a test with one malformed record for each read command).

2. **Design gap: a blocking review can never be resolved without editing content or deleting the review file** (lines 118-123). Any `changes_requested` review on the current digest blocks acceptance forever, even if the same reviewer later files `approved` on the same content. Reproduced with the fixture: adding a `changes_requested` copy of the existing approved review → `accepted finding has an unresolved blocking review`. The practical way out is deleting the blocking record, which the validator cannot see (only Git history shows it). Suggest: a later review by the same reviewer supersedes their earlier one (needs a `created_at` or a `supersedes` field), and a test that deleting a review record is caught in PR review, not by the validator.

3. **Minor: dead code** — line 223 re-checks `args.command == 'digest'`, which already returned at line 205.

4. **Minor: `bundle()` trusts `evidence` type** (line 166). If `evidence` is a string, `list()` splits it into characters and the export silently omits the file; if it is a number, `export` exits with a `TypeError`. `validate` catches this, but `export` only warns. Use the same list check as `validate`.

5. **Minor: search matches the text `None`** — `values()` turns `null` fields into `"None"`, so `search none` matches records with null fields.

6. **Note, not a bug:** a `skill` can be `released` with no review record, and `permissions` can be an empty list or non-strings. Fine for a PoC; say so in the README or require a review for `released`.

7. **CI:** looks right (`contents: read`, 3.9 + 3.13 matrix, runs both Python suites and the Node tests). Optional hardening: pin actions to commit SHAs and set `persist-credentials: false` on checkout.

## What I did not review

The issue template wording and the fixture records' prose; the `BOARD.md` / `README.md` edits on that branch (they may conflict with `claude/round-lifecycle`'s board edits when both merge).
