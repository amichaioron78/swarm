# FONT-DIGITS-69-1 — isolated successor to Claude d1b

Date: 2026-10-31. Owner: GPT, derivative experiment only. Parent task FB-002 stays
with Claude; canonical sources and release fonts are untouched. Rubric unchanged.
No score, peer approval, merge or owner visual acceptance is claimed.

## Actual change

The d1b source uses a tuned cubic approximation for the ellipse head, but attaches
the tail using the tangent of a mathematical ellipse. This is a likely cause of its
recorded six/nine outer kink and counter step. The trial uses the existing arc
primitive for a complete closed head, split at the tail attachment angle. Its local
point and derivative now agree with the tangent used by the tail. Six remains the
180-degree rotation of nine. No reference contours are copied into the candidate.
The head curvature changes slightly as a consequence; it is not merely a local
point move. Visual acceptance of that change is still needed.

## Reproduction and validation

Recovered the actual d1b source and fonts from the canonical private snapshot after
workspace maintenance removed the local copies. Library search did not resolve the
project artifacts; existing private Drive snapshots supplied them. All six files in
Claude's manifest match. The unchanged six/nine source reproduces the original
quantized coordinates, contour endpoints and flags exactly, in both weights.

The first reconstruction attempt omitted the existing outer builder's 0.88 numeral
scale. The guard caught the mismatch and stopped before output. Restoring that
existing pipeline factor yielded exact geometry. Preserve this failed attempt as a
reminder to recover the whole call chain rather than inferring parameters from names.

Only six/nine outlines change in each actual 60-glyph font. All other 58 glyph
outlines, horizontal metrics, coverage, layout and global hint tables match d1b,
verified with the release comparator from PR #6. Candidate glyph instructions are
removed only for these two trial glyphs; the before control removes those same two
instructions. Native-size comparison therefore does not mix hinted and unhinted
six/nine. These are prototypes, not a rehinted production build. Trial metadata
identifies them separately to avoid cache confusion.

Eight reconstruction guard checks pass on actual fonts, including one-unit injected
coordinate errors. Both actual-font release isolation checks pass. All six artifact
checksums pass; both trial fonts load and rasterize. Python compile check passes on
Linux Python 3.12, fonttools and skia-pathops. Previous Mac/legacy test counts are
not repeated as current results; no Mac environment is available in this batch.

## Visual observations and remaining work

Matched 128/48/24/16ppem diagnostic inspected in Regular/Bold. The enlarged join
appears smoother to GPT; the small-size difference is subtle and does not establish
a readability gain. Existing private d1b/Polin reference sheet was inspected, but
there is no newly rendered matched Polin panel here. No Polin equivalence is claimed.
Other numeral issues and the pending qof decision remain outside this experiment.

Next: one bounded Claude review of these exact source/font hashes, then authorized
full rebuild/rehinting and matched benchmark comparison if this direction survives
peer and owner visual review. Do not integrate this trial into the canonical release.

## Reusable implementation and lesson

`reconstruction_guard.py` is called by the private trial builder. It refuses a source
reconstruction whose coordinates, contour endpoints or point flags differ from the
existing glyph. It deliberately excludes hints and says so. Pair that guard with
release table isolation and actual rendered output; none alone establishes typography
quality. A theoretically tangent line is not enough if the drawn primitive uses a
different approximation or does not share the actual attachment point/derivative.

Both usage dashboards remain inaccessible. This was one bounded implementation
batch with no extra agents, purchases, permission changes or review polling loop.
