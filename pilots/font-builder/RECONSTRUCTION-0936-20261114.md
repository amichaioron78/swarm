# Existing 0.936 component reconstruction — 14 November 2026

FONT-0936-RECON-1, GPT. Geometry replay only, not a full release or visual score.
Rubric v1 remains frozen and proposed. Canonical source/output is unchanged.

## Concrete result

Recovered the existing m4 mem and d3 numeral source; reused previously recovered
r5 pe/finalpe source and original outline primitives. Source files match their
private round manifests; dependency modules match the baseline manifest. Actual
0.936 font inputs retain their release hashes. No reference contours were read
or copied and no new glyph design was introduced.

Using saved measured parameters and the existing builder's Optical width, spacing,
cubic-to-quadratic and numeral integer-centering rules, reconstructed all 13
changed outlines (mem, pe, finalpe, zero–nine) in both Regular and Bold. ALL 26
match the actual 0.936 glyph point coordinates, contour endpoints and point flags.
Records were generated from source functions, not extracted from output contours.

Mem's raw and unioned replay both match, so union is not needed to explain that
particular output. Pe/finalpe replay uses the builder's winding normalization and
path union. Numerals preserve conversion THEN integer centering; moving the shift
before coordinate rounding can change the result. Keep that order when integrating.

This resolves the previously unknown component-outline reconstruction. It does
NOT reproduce the entire font, metrics, name tables, hint programs or final bytes.
No full build or reproducible release claimed. Original 0.935 build entrypoint is
still not a canonical 0.936 entrypoint. Source wrappers would write default output
paths: they were inspected, NOT executed. Only isolated mathematical definitions
were evaluated; no licensed font installation is required for this narrow replay.

## Implementation and verification

`verify_components.py` takes private source-derived recording-pen components,
requires an explicit exact glyph set (no duplicates/omissions), compiles using
existing `trial_glyph.compile_records`, applies integer post-quantization shifts,
and invokes the existing strict geometry guard. It logs font/records hashes and
states its limited scope. It does not modify a font or generate an automatic score.
Private replay scripts, records, inputs, source pins and reports are retained for
peer review; they are not embedded in this public repository.

Validation on Linux Python 3.12.14:

- 26/26 actual glyph reconstructions match in both styles.
- Eight injected failures rejected: a source-point displacement, numeral shift,
  missing requested component and duplicate component, each in Regular/Bold.
- 12 legacy Python tests pass; compilation and whitespace checks pass.
- Missing skia-pathops dependency initially blocked numeral replay; installed the
  ordinary dependency, then reran successfully. No geometry mismatch hidden.
- Mac Python 3.9/3.13, benchmark comparison and full hinting/build remain unverified.

## Coordination and next task

Fresh AGENTS/BOARD, remote state, font Kanban, open PR list and forum were read.
The latest mailbox receipt is received, not completed review. Existing substantive
review request remains pending; no duplicate request or polling loop initiated.
Detailed private mailbox content stays private. No infrastructure work undertaken.

Next: a source-capable writer can use the replay bundle to create the canonical
0.936 build entrypoint, validate complete metrics/hinting and compare complete
output before reviewed integration. Numeric bearings, small-size Bold density,
Polin/Mac comparison, earlier qof trial, alef/zayin requests and owner family visual
acceptance remain open. Passing reconstruction is not 10/10 typography.

Usage dashboard browser unavailable before/after; no account readings, reliable
provider daily denominator or project attribution. One bounded reconstruction task,
no new review request. No hard 10% cap claim. No merge or installation.
