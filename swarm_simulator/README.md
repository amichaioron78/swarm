# Swarm simulator 0.2

An interactive simulator for Swarm's two-team/referee architecture, prepared for Vercel. Includes an actual two-agent source-repair test case, with Claude's verdict explicitly pending until real access is available.

## Run

Requires Node 20+. No dependencies, API keys or installation required for simulation.

```sh
npm test
npm run build
```

Serve `dist/` using any static HTTP server. The app uses ES modules, so open it over HTTP rather than double-clicking the HTML file.

## Vercel

Import this directory as a project, choose Other as the framework, and use the included `vercel.json`. Build command: `npm run build`. Output directory: `dist`. Alternatively, with an authenticated Vercel CLI, run `vercel` from this directory. No environment variables are needed for the simulator. Deployment has not been completed until a verified Vercel URL is returned.

## What works

- Two competing teams, a separately allocated referee budget and equal contributions.
- Seeded scenarios for marketing, research and coding.
- Start, pause, step and reset; change membership, budget, seed and sharing.
- Budget ledger, team and individual scores, graph, event log and shared findings.
- Member departure and illustrative 183-day access freeze.
- JSON export for reproducibility.
- Actual agent-test status and source artifacts packaged separately.

## Simulation boundaries

The simulator runs entirely in the browser and stops when the page closes. Configuration and findings reset on reload. Work units and outcomes are synthetic. Model names are labels. Hard-coded sharing/diversity effects are illustrative assumptions, not measured model advantages. This does not run agents, transfer subscription allowances, train models or create real clients.

The real test case was run separately by two ChatGPT agents given the same repair task. Their candidate code and test evidence are under `contest/` in this package. No model usage receipts are available, so this is not an equal-compute benchmark. Claude has not judged the submissions; no winner is declared. The browser's membership and spending rules are not a production security boundary.

For continuous real execution, the next system requires authenticated provider adapters, a durable job queue and database, atomic budget reservations, isolated execution and a Claude referee connection. Do not place provider API keys in browser code.
