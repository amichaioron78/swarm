# FONT-QOF-1 — existing-font terminal trial, 28 October 2026

Status: private visual candidate, not an accepted font release. Owner request FB-003.
Related mission #3; discussion #2; builds on FONT-BASELINE-1 and its proposed rubric.
The rubric is unchanged. No score or improvement acceptance is assigned.

## Result

Recovered measured parameters plus the original source reconstruct the unhinted
baseline ק exactly in Regular and Bold (compiled glyph bytes match). An isolated
candidate shortens the leftward bowl extension, narrows the terminal and points it
more downward. Roof, detached leg and all horizontal metrics remain unchanged.
Only ק changes in the two actual existing-font copies; all 59 other glyphs retain
their compiled data. This is source-derived font work, not a substitute alphabet.

An unhinted baseline is compared with an unhinted candidate so hinting is not an
uncontrolled variable. The actual hinted release is not overwritten. Full pipeline
rebuild, rehinting and the mandated Polin comparison remain pending. No reference
binary was obtained or substituted; project source and specimens remain private.

## Attempts retained

- A: rejected on visual inspection for a pointed terminal and Bold kink.
- B: rejected on visual inspection for a detached sliver caused by crossing return
  geometry. Compilation and glyph-isolation checks did not detect this visual failure.
- C: review candidate with consistent boundary ordering and a flat narrow bottom
  cut. GPT visually inspected matched diagnostic renders at 160/48/24/16ppem.
  More open bowl and shorter leftward extension change the letter's character;
  whether this meets the owner's intent remains an explicit design decision.

## Checks performed

Linux Python 3.12, fonttools 4.61.1, skia-pathops 0.9.2, Pillow RAQM.
Eight actual-font checks pass (four per weight): single-glyph isolation and identical
metrics; output overwrite rejected; mismatched reconstruction rejected; unchanged
candidate rejected. Both source reconstructions are byte-exact against the retrieved
unhinted release fonts, whose hashes match the release manifest. Compile check and
12 existing Swarm Python tests pass. Mac Python 3.9/3.13 not available here.

`trial_glyph.py` is the reusable implementation: given private old/new recording-pen
JSON, it requires exact baseline reconstruction and writes a new single-glyph font
copy. It refuses overwrites and unexpected outline/metric changes. It does not
establish shaping, kerning, contour topology or visual quality. Keep its outputs
private when the input font is private.

## Reusable finding (proposed; independent review pending)

For an existing-font glyph prototype, reconstruct the unchanged source glyph before
editing and pin the actual font bytes. This can isolate a design test when a full
build needs unavailable licensed metrics. It does not replace the release build.
Boolean simplification can turn crossed boundaries into valid-looking separate
contours, so a compiling font and a one-glyph diff still require visual inspection.
Preserve the failed output as evidence rather than declaring the test a quality pass.

## Handoff and next step

The prior Claude request has no receipt or response as of this check. Supplement it
with the actual private specimens and trial sources, without creating a second
review loop. Reviewer must check C against the owner's brief and Polin at identical
settings; inspect small-size rhythm and terminal shape. Owner visual acceptance,
peer review and integration remain pending. No merge was performed.

Usage dashboard access remains unavailable for both providers in this run; no daily
percentage is inferred. Work stopped after this bounded glyph batch.
