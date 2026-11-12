# Swarm — task board

Owner: GPT / Claude / Amichai · Status: todo / doing / review / done
Agreed between Claude and GPT on 2026-10-25 (see .bridge/conversation.md).

| # | Task | Owner | Status | Notes |
|---|------|-------|--------|-------|
| 1 | Python 3.9 compatibility (`from __future__ import annotations`) | Claude | done | 12/12 on /usr/bin/python3 3.9.6 and Homebrew 3.13 |
| 2 | Round lifecycle: stable round IDs, `end_round()` + `next_round()`, membership changes between rounds, rejoin after cooldown, per-round allocation so already-spent units never become spendable again | Claude | review | Branch `claude/round-lifecycle` (2026-11-12): `round_id`, `rounds`, `available()`, `end_round()`, `next_round()`, `round_summary()`, per-round `scoreboard(round_id)`; results tagged with round. New rounds allocate only never-spent units; unspent units carry over. debit() untouched (#3). Tests in own class `RoundLifecycleTests`. Cloud-only test run; Mac two-Python run still needed. Not merged |
| 3 | Per-owner metering: debit() attributed to owner/worker and round ID; operation IDs so a retried debit is not charged twice; explicit attribution for referee spending | GPT | todo — can start from `claude/round-lifecycle` (`self.round_id` is the round ID to attach to debits) | Review #5 + GPT's idempotency finding. Touches debit() + new ledger structure |
| 4 | Rule for a team that empties mid-round | Amichai to decide | todo | Review #3 |
| 5 | Can members who left still receive points (e.g. for work done before leaving)? | Amichai to decide | todo | Review #4; code can't yet tell when work happened |
| 6 | Encode 30% capacity policy + 18:00–06:00 worker window | unassigned | todo | Review #6 |
| 7 | Store and version the "locked rubric" per round; enforce it | unassigned | todo | GPT finding |
| 8 | Split ownership of test_swarm.py and the demo to avoid edit conflicts | Claude + GPT | todo | Proposal: each adds tests in its own TestCase class |
