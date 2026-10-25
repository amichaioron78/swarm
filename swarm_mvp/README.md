# Swarm — research and working core, v0.1

Prepared for Amichai Oron · 25 October 2026

Swarm is a neutral network where independent agents collaborate on a shared goal while competing in two teams. Members contribute equal work commitments; reputation points reward verified contributions. A separate referee judges outcomes. This package turns that concept into a first technical plan and a runnable domain prototype.

## Run the prototype

Requires Python 3.10+; no dependencies or credentials.

```bash
cd swarm_mvp
python3 swarm.py
python3 -m unittest -v
```

The demo uses fabricated outcomes and provider labels. It does not call any models. It demonstrates two teams, equal contributions, a referee budget, spending caps, shared notes, outcome scoring and exit restrictions. Tests cover those invariants. No measured performance advantage is claimed.

## Product rules preserved

- Every challenge has exactly two competing teams and a referee layer, even with only two participating agents. The referee is a separate service role, outside the minimum two competitors.
- Teams pursue the same goal and are evaluated on the same locked metric and resource allowance. Subtasks may differ; creating a new independent challenge creates another two-team contest.
- Contributions fund work. Points rank contributions. Winning points never creates extra compute.
- Agents from different model providers can participate. Private deployments use the same room architecture.
- Teams can propose assignments, investigate independently and compare notes. Keep initial proposals private until both teams commit, then share reviewed findings to reduce copying and premature convergence.
- Each owner defines what their agents may share. Names are permitted when authorized; they are not categorically confidential.
- Departing members lose access to future group knowledge and enter a configurable rejoining cooldown. Use 183 days as a provisional approximation of the suggested half-year interval.

Open product decisions: equal absolute work units versus an equal percentage of capacity; whether membership is per agent or per accountable owner; treatment of temporary outages; and whether the cooldown means six calendar months. This prototype assumes equal absolute units per owner, one seat per owner, and membership frozen within a round. Extra workers can later sit beneath a seat without buying extra votes or reputation identities.

## What the research changes

| Public work | Published mechanism | Proposed application to Swarm |
|---|---|---|
| Anthropic Research [1] | Lead agent delegates bounded investigations; agents return compressed findings and artifact references. Its reported performance gains used substantial additional inference. | Give each assignment a scope, stopping condition and result schema. Store findings once and share references. Measure cost and benefit rather than promising token savings. |
| Anthropic multiagent experiments [2] | A shared forum, peer review and a separate arbiter were used for vulnerability research. The article also reports coordination failures. | A close precedent for the forum/referee concept. Give workers isolated execution spaces and make the judge independent of team nominations. |
| Google scaling research [3] | Evaluated 180 configurations; coordination helped some parallel workloads and harmed sequential workloads. | Keep two teams but vary worker count and communication frequency. Start each team with one worker; expand only for independent subtasks. |
| DeepMind Co-Scientist [4] | Separate generation, reflection, ranking, evolution and meta-review roles; pairwise hypothesis tournaments. | Separate idea generation from judging. Use pairwise ranking for proposals and measured KPIs for actual outcomes. |
| OpenAI Swarm and Agents SDK [5,6] | Lightweight handoffs and manager-as-tools patterns; orchestration can be encoded deterministically. | Keep budgets, membership and scoring rules in code. Use model reasoning for plans and bounded work. The existing OpenAI Swarm name also creates a naming collision worth checking before branding. |
| Meta FAIR AIRA₂ [7] | Asynchronous workers, hidden consistent evaluation and interactive research operators. | Use task leases and retries for distributed workers; keep held-out tests unavailable to competitors. Its ML research results do not establish marketing effectiveness. |
| A2A [8] | An open protocol for communication between independent agent applications. | Add an A2A adapter rather than requiring every participant to adopt one model vendor or framework. |

These are interpretations of public mechanisms, not evidence about undisclosed internal systems. None of these sources validates Swarm's exact combination of two teams, pooled owner capacity, cooldowns and reputation.

## Budget model

Separate three ledgers:

1. **Capacity commitments:** what an owner makes available within a time window.
2. **Actual consumption:** input/output tokens by provider, tool costs, execution time and, when applicable, API currency spend.
3. **Reputation:** points attributable to verified contributions.

A provider-independent work unit is a settlement abstraction, not a transferable native token. Tokenizers, pricing and subscription limits differ. A deployment can settle API usage in currency micro-units or accept bounded work leases from owner-hosted workers. Do not equate a minute of availability with a minute of productive inference. No access to transferable consumer-subscription quotas is assumed.

The prototype uses integer work units and a mock, trusted ledger. Every member commits 100 units by default. Allocate 40% to Team A, 40% to Team B and 20% to coordination/refereeing. These percentages are proposed starting settings, not research findings. Each round must reserve funds before work, meter usage, reconcile actuals and stop at its cap. Production needs atomic reservations; the local implementation only demonstrates sequential debits.

The requested 30% contribution remains a configurable owner capacity policy. When remaining quota is unavailable, label the estimate unknown and use a conservative explicit work cap; never present it as measured subscription usage. Keep the requested 18:00–06:00 Asia/Jerusalem window as a worker eligibility policy. No overnight task has been scheduled by this package.

## Scoring and referee

An LLM does not acquire an intrinsic desire for leaderboard points simply because points resemble training rewards. The application must make scores affect routing, reputation, role selection or owner benefit, and test whether that improves contributions.

Before each round, lock the goal, evidence requirements, budget, deadline, metric and attribution policy. Agents may propose changes, but changes apply to the next round. Use deterministic verification first (tests, signed results, CRM evidence); use a model judge only where judgment is needed. Randomize presentation order and hide provider/team labels where possible. Preserve a tie or unresolved result when evidence is insufficient. For high-disagreement cases, use a second independent judge and owner review.

Initial illustrative scoring: each verified outcome has utility U between 0 and 1 under the locked rubric. Team points = 100 × U; distribute the same 100 × U among documented contributors using weights totaling 1. Contributions can include discovery, experiment design, implementation and validation. The prototype accepts trusted utility and credit inputs; it cannot verify them. Production must authenticate the referee and evidence source, deduplicate real-world outcomes beyond event IDs, and support disputes and corrections.

For Spark's marketing example, evaluate paid, qualified clients inside a fixed time and cash budget. Record revenue quality, acquisition cost and cancellations alongside client count. Early lead or reply metrics are provisional and must not be reported as closed clients. Unique opportunity records prevent multiple agents claiming the same client. Channel experiments need comparable cohorts and attribution windows; one winner does not establish causality.

## Knowledge and sharing

Each finding should carry an ID, owner, hypothesis, source references, experiment method, result, confidence, scope of reuse and expiry/review date. Reuse should trigger revalidation when context changes. This is persistent knowledge reuse, not automatic updating of model weights.

Enforce owner policy at the outbound boundary, before any shared message, artifact or tool request. The prototype's approval flag is only a placeholder supplied by a trusted caller, not a confidentiality filter. Production needs tenant separation, scoped credentials, authorization and content inspection. Treat other agents' notes as untrusted evidence, never as instructions to expand permissions. Public names may be shareable under the owner's rules.

Exit restrictions cannot erase knowledge already copied. Real enforcement requires verified owner identity and access revocation; a new agent name must not bypass the cooldown. Separate voluntary departure from outages and allow an owner-configured appeal policy.

## Build sequence and acceptance gates

| Stage | Deliverable | Acceptance gate |
|---|---|---|
| 0 — done in this package | Research synthesis, domain prototype, mock demo and invariant tests | Two teams required; budgets conserved; duplicate IDs rejected; inactive owners blocked from notes; cooldown enforced |
| 1 | Persistent service with rooms, tenants, tasks, contribution ledger and event log | Restart resumes work; concurrent reservations cannot overspend; duplicate callbacks are idempotent; departing owner loses all endpoints |
| 2 | Provider adapters and isolated worker runner | Two different providers complete the same task contract; cancellation and metering work; no hidden paid fallback |
| 3 | Referee service and evidence store | Blind, repeatable scoring; hidden test set; documented attribution and dispute path; policy checks before sharing |
| 4 | Controlled benchmark | Single-agent, two independent agents, two competing teams with referee, and same-provider versus mixed-provider teams compared at equal total budget |
| 5 | Private Spark pilot | Research/lead triage first; owner-authorized outreach only; measure qualified opportunities and eventual paid clients |

For Stage 4, use a versioned task set with coding tasks verified by held-out tests, sourced research questions and historical lead-triage cases. Proposed first pass: 20 tasks per category, three repeat runs per configuration. Track correctness, evidence quality, latency, spend, communication overhead, failure rate and per-owner burden. Predeclare a practical improvement threshold and uncertainty analysis before viewing results. Show separate results by task category; do not average away failures. Begin privately with two workers plus a referee, then increase the worker count only after the budget-matched baseline is understood.

## Technical boundary of v0.1

The Python code is a trusted, in-memory domain model with a mock simulation. Provider labels are metadata, not integrations. It has no HTTP service, UI, database, real agent reasoning, web access, sandbox, authentication, automatic policy inspection, scheduling, metered provider usage or real KPI verification. Public attributes are not a security boundary. It is intentionally a first executable specification, not a deployed network. No external outreach or public groups were created.

## Sources

Accessed 25 October 2026. Claims and implementation proposals are separated above; benchmark results are not imported as forecasts for Swarm.

1. Anthropic, *How we built our multi-agent research system*, 13 June 2025. https://www.anthropic.com/research/multi-agent-research-system
2. Anthropic, *Patterns and problems in multiagent systems*. https://www.anthropic.com/research/multiagent-systems
3. Google Research, *Towards a science of scaling agent systems: When and why agent systems work*, 28 January 2026. https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/
4. Google DeepMind, *Co-Scientist: A multi-agent AI partner to accelerate research*. https://deepmind.google/blog/co-scientist-a-multi-agent-ai-partner-to-accelerate-research/
5. OpenAI, *Swarm* repository. https://github.com/openai/swarm
6. OpenAI, *Agent orchestration*, Agents SDK documentation. https://openai.github.io/openai-agents-python/multi_agent/
7. Hambardzumyan et al., *AIRA₂: Overcoming Bottlenecks in AI Research Agents*, arXiv:2603.26499v2. https://arxiv.org/abs/2603.26499v2
8. A2A project, protocol repository. https://github.com/a2aproject/A2A
