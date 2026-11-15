# Zero stroke-weight trials — 15 November 2026

FONT-ZERO-WEIGHT-1, GPT. Frozen proposed rubric v1 unchanged; no score or integration.

The actual-font comparison found zero's mid-height side stroke at 72/134 units
(Regular/Bold), beside vav at 90/168. Existing numeral source contains cumulative
reductions: builder 0.88 then numeral 0.90. This is verified source behavior, not
proof that either reduction is an accidental bug. Retain the design decision for review.

## One bounded experiment

Reused the existing d3 zero function and original ellipse/stroke primitives in a
private isolated snapshot; no contour tracing or benchmark outlines copied.
Two parameter variants multiply both pen dimensions by 1.125 (A) and 1.25 (B).
The zero ellipse remains the original shape and size: 540-unit advance, outer
bounds and overshoot unchanged. Both weights source-reconstruct the current zero
exactly before editing. All other 59 glyph outlines and horizontal metrics are
unchanged. Control AND candidate remove glyph hints equally; release fonts untouched.

| Side stroke, units | Baseline | A | B | Existing vav |
|---|---:|---:|---:|---:|
| Regular | 72 | 81 | 90 | 90 |
| Bold | 134 | 150 | 167 | 168 |

Matched actual-font specimens at native 12/16/24/48/96 pixels compare baseline,
A, B and the licensed private Polin reference. Polin uses its original CFF hints;
small-size comparisons against it are platform/render evidence, not hint parity.

## Visual finding and unresolved fork

B visibly closes the zero/letter stroke gap at display size, but also makes zero
heavier than the untouched adjacent numerals. A is an intermediate compromise.
Neither is approved as a release improvement. In Bold, B narrows the counter and
looks dense; small-size quality is unresolved. Increasing a single numeral's weight
cannot fix the full numeral system. No peer verdict or disagreement received yet;
owner choice and whole-number rhythm review remain outstanding. Other nine digits,
coverage, niqqud/Latin/currency, Semibold, alef/zayin/qof/shin requests, build/hint
provenance and target-platform review remain open.

## Implementation and evidence

`trial_component.py` adds an isolated source-record trial compiler: exact geometry
guard, integer post-quantization centering, fresh destination, matched unhinted
controls, serialized non-target outline/metric checks. Private scripts, parameters,
records, candidates and hashes are retained with specimens for review. No licensed
font binaries or private project source are included in this public repository.

Validation: four actual-font trials pass geometry reconstruction/isolation, exact
outer bounds and two-contour preservation. Eight negative controls reject source
point mismatch, no-op, different target and existing destination across both weights.
12 legacy Python tests pass on Linux Python 3.12.14; compilation/whitespace pass.
Mac Python 3.9/3.13 checks unavailable. Missing skia-pathops initially blocked the
run; ordinary dependency installation succeeded. First large specimen overflowed
its columns; split long 96px digit rows and re-rendered before delivery.

Metering: connected browser unavailable before work; no new authorized dashboard
surface appeared afterward. No provider readings or daily denominator/attribution.
One implementation task, at most one bounded evidence/review handoff; no polling.
Prior PRs #4–#10 remain draft/unmerged. No release installed or merged.

Next: peer/owner compare A/B in complete numeral rhythm, then choose a bounded
family-wide numeral-weight proposal before integration. Keep full build work open.
