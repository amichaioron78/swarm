# Validation — 2026-10-27

Environment: Linux Python 3.12; fonttools 4.61.1, Pillow 12.3.0 with RAQM.

- Audited both recovered current TTFs; every table decoded.
- Both fonts: 60 glyphs; required 27 Hebrew letters, digits and punctuation present;
  no niqqud; no variable axes; GPOS present (not verified here).
- Baseline Regular compared to itself: zero changed glyphs.
- Two output + three current source hashes match the release manifest: 5/5.
- Rendered and inspected private baseline diagnostic at 16/24/48/72ppem.
  No benchmark comparison, glyph change, visual score or rebuild claimed.
- python3 -m unittest discover -s swarm_mvp -v: 12/12 pass.
- python3 -m py_compile pilots/font-builder/audit_font.py: pass.
- git diff --check: pass.

Pending: Mac Python 3.9/3.13; full source rebuild; actual Polin comparisons;
Claude peer review and owner acceptance. Existing build remeasures licensed local
Ploni/Polin fonts and requires native dependencies not available here.

Failure retained: streamed binary downloads stalled; bounded inline download of
these small TTFs succeeded and release hashes confirmed bytes.

Next: verify the build in the canonical font environment; select one owner glyph
request; render matched baseline/candidate/Polin panels. Preserve old rejected
thinning and inconclusive hinting attempts rather than treating them as proven fixes.
