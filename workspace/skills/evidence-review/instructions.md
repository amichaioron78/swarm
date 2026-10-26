# Evidence review workflow, version 0.1.0

Purpose: help an agent act as a peer reviewer of a finding. This is a downloadable product fixture, not an installed ChatGPT skill or an executing program.

1. Read the proposed finding, evidence files and linked experiment.
2. Check that the claim follows from the evidence and states limitations.
3. Check previous contradictory findings and relevant failed attempts.
4. State which checks you actually performed; distinguish synthetic examples from real results.
5. Return approve, changes requested, or comment, with reasons. Record the target content digest and your agent label. Do not review your own work as independent approval.
6. A review does not grant merge authority, owner consent or new tool access.

Required permissions: repository read access. No network, account credentials or execution required. Known limitation: an agent label is not verified identity.
