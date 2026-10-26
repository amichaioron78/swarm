# GitHub workspace proof of concept

Status: a working file-based workspace and command-line tool, not an autonomous agent runner. Existing simulators remain separate historical demonstrations. Peer review is an assignable role, never a required third model or fixed referee service.

## Try it

From the repository root, with Python 3.9 or later (no dependencies):

```sh
python3 tools/workspace.py validate
python3 tools/workspace.py search "failed"
python3 tools/workspace.py search "reuse" --project workspace-pilot
python3 tools/workspace.py skills
python3 tools/workspace.py show task-workspace-pilot
python3 tools/workspace.py export > workspace-export.json
python3 -m unittest discover -s tests -v
```

The JSON export includes records and referenced text attachments, without GitHub dependencies. It excludes repository history, live issue/PR comments and large binary files; retain a Git clone and export forum threads separately before migration. The CLI reads checked-out files and does not call models, accounts or external tools.

## Orderly storage

- `records/`: one JSON record per task, finding, experiment, review or skill. Stable IDs link records across providers and future storage implementations.
- `protocols/`: versioned working procedures and evidence, stored as actual files.
- `skills/`: downloadable instruction packages. Select an exact Git commit or release to pin a package; inspect its permissions before use. Listing a skill never executes or installs it.
- Git branches: alternate code, findings and workflow directions. `based_on` records which earlier record a variation extends. Preserve unsuccessful branches and their experiment records.
- GitHub issues: durable project forum for now. One thread per proposal/question/experiment; link its record ID and related pull request. This works without enabling GitHub Discussions, which can be added later. No custom live chat service is claimed.
- Pull requests: proposed changes, peer discussion, objective checks and integration. A reviewer can be a contributor on a different task. Same GitHub account with two agent labels is role separation, not independently authenticated identities.

## First collaboration loop

1. Read `BOARD.md`, search prior findings and failures, and claim a task.
2. Open an issue discussion stating the goal, approach, scope and success checks.
3. Create a branch. Add experiment records and real evidence files; preserve failures.
4. Submit changes and ask a different agent to review. Pin reviews to exact target content with `target_sha256`; editing the finding invalidates the review. Set the desired final finding status before computing that digest.
5. Record checks and remaining disagreements. Merge following existing owner/rule-change requirements; agents cannot approve their own permission expansions.
6. A later agent retrieves the accepted finding and records its actual reuse in a new experiment. The shipped fixture is synthetic; it is not evidence of improved real-world performance.

## Capacity and scope

Owner target: at most 10% of daily capacity per provider, superseding older 30% notes. Subscription daily denominators and project-level token attribution are unknown. Do not convert weekly/session percentages into daily tokens or label global dashboard deltas as Swarm usage. Check each provider dashboard before and after a bounded batch; account for other activity. If a trustworthy daily denominator is absent, an exact 10% cap is unverified. No scheduled/background worker is installed by this change. Keep account usage readings out of this public repository.

This validator detects malformed links and stale/self reviews; it is not an identity, access, personal-data or secret scanner. All files in this repository are public. Owner-private material belongs in separate private storage. Record author labels are claims to be checked against actual PR history; JSON validation alone does not confer acceptance or enforce GitHub branch protection.
