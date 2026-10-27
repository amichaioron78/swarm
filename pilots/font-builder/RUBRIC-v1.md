# Proposed font quality rubric v1 — frozen for the first pilot batch

Status: proposal awaiting Claude review and Amichai's acceptance. No score assigned.
Freeze date: 2026-10-27. Changes require a new version, rationale, and owner agreement;
reassess baseline and candidate together. Never change thresholds to manufacture a pass.

| Dimension | Points | Evidence needed for full marks |
|---|---:|---|
| Glyph construction and shared components | 2 | All 27 Hebrew letters and 10 digits; inspect joins, terminals, counters and recurring members in both weights; resolve specific owner requests |
| Optical proportions | 2 | Matched benchmark panels; coherent stroke color, counter area, round overshoot and diagonal weight; no unexplained outliers |
| Spacing, kerning and Hebrew rhythm | 2 | Words, paragraphs, difficult pairs, final forms, punctuation and mixed numbers; inspect with shaping enabled; measurements support visual review |
| Weight/width behavior | 1 | Verify implemented styles/axes and shared family identity; if variable fonts are supported inspect extremes and intermediate instances for collisions and contour failures |
| Multi-size readability | 2 | Matched 12/16/24/48/96px text in Regular/Bold, actual ppem logged; inspect native-size and enlarged output; no missing-glyph substitution |
| Technical export integrity | 1 | Reload all tables, correct names/version/cmap/metrics, shaping/rasterization and supported export formats; explicitly record omitted coverage |

Each dimension: 0 = unverified or material defects, half credit = demonstrated but
unresolved defects, full credit = all evidence reviewed with no unresolved issue.
Unknown evidence remains unassessed, never silently full credit. No automatic total.
The rubric is a review guide, not a claim that typography has an objective perfect score.
10/10 requires independent output review plus Amichai's explicit final visual acceptance.

Current recovered requirements: Oron first, Polin immediately below at identical
text, weight and displayed size; order sample line, all Hebrew letters, digits,
short sentences. Polin and Ploni are distinct references. Never substitute a
fallback or infer that old Tirgul interpolation masters apply to current static fonts.
Niqqud scope remains explicit; lack of niqqud cannot be called complete pointed Hebrew.

Private sources and licensed benchmark binaries must stay outside this public repo.
No scores from old anonymous reviews constitute current owner acceptance.
