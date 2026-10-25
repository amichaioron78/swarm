# Swarm — task board

Owner: GPT / Claude / Amichai · Status: todo / doing / review / done

| # | Task | Owner | Status | Notes |
|---|------|-------|--------|-------|
| 1 | Python 3.9 compatibility (`from __future__ import annotations`) | Claude | done | Tests pass on this Mac's python3 3.9.6 |
| 2 | Round lifecycle: `end_round()` + `next_round()`, membership changes between rounds, rejoin after cooldown | Claude | todo | Review finding #2 |
| 3 | Per-owner metering: `debit()` records which owner/worker spent units | GPT (proposed) | todo | Review finding #5 — needed for Stage 4 |
| 4 | Rule for a team that empties mid-round | Amichai to decide | todo | Review finding #3 |
| 5 | Can members who left still receive points? | Amichai to decide | todo | Review finding #4 |
| 6 | Encode 30% capacity policy + 18:00–06:00 worker window | unassigned | todo | Review finding #6 |
