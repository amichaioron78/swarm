# Swarm — task board

Owner: GPT / Claude / Amichai · Status: todo / doing / review / done
Agreed between Claude and GPT on 2026-10-25 (see .bridge/conversation.md).

| # | Task | Owner | Status | Notes |
|---|------|-------|--------|-------|
| 1 | Python 3.9 compatibility (`from __future__ import annotations`) | Claude | done | 12/12 on /usr/bin/python3 3.9.6 and Homebrew 3.13 |
| 2 | Round lifecycle: stable round IDs, `end_round()` + `next_round()`, membership changes between rounds, rejoin after cooldown, per-round allocation so already-spent units never become spendable again | Claude | todo | Review #2 + GPT's "cumulative pool" finding. Touches join()/start() + new methods only |
| 3 | Per-owner metering: debit() attributed to owner/worker and round ID; operation IDs so a retried debit is not charged twice; explicit attribution for referee spending | GPT | todo — starts after #2 lands (needs round IDs) | Review #5 + GPT's idempotency finding. Touches debit() + new ledger structure |
| 4 | Rule for a team that empties mid-round | Amichai to decide | todo | Review #3 |
| 5 | Can members who left still receive points (e.g. for work done before leaving)? | Amichai to decide | todo | Review #4; code can't yet tell when work happened |
| 6 | Encode 30% capacity policy + 18:00–06:00 worker window | unassigned | todo | Review #6 |
| 7 | Store and version the "locked rubric" per round; enforce it | unassigned | todo | GPT finding |
| 8 | Split ownership of test_swarm.py and the demo to avoid edit conflicts | Claude + GPT | todo | Proposal: each adds tests in its own TestCase class |

## GitHub workspace proof of concept — 26 October 2026

| ID | Task | Owner | Status | Scope |
|---|---|---|---|---|
| POC-1 | Portable records, search/export/validation CLI, workflow examples and checks | GPT | review | New workspace/ and tools/ files only; branch poc/github-workspace |
| POC-2 | Independent peer review of POC-1 and usage check | Claude | done | Changes requested on 1786631; findings addressed and disagreement retained in workspace/protocols/peer-review-2026-10-26.md; final revision not re-reviewed |

Current owner direction: GitHub first; competition optional; peer review is a task role. Latest capacity target is 10%, replacing the earlier 30% target. Exact daily subscription capacity and task attribution are unavailable, so do not claim an enforced percentage. This batch is bounded to implementation and one review; no recurring runner is installed. Private usage readings stay outside this public repository.
