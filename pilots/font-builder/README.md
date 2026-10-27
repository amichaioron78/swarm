# Existing font pilot

Mission: issue #3. Coordination forum: issue #2. This extends the existing Font
Generator; it contains no replacement font or copied reference contours.

`audit_font.py` reads an actual local TTF/OTF, pins its bytes, records individual
glyph outlines/bearings and reports missing coverage. With `--candidate` it lists
changed glyphs. Requires fonttools; does not call models or read accounts.
Keep JSON output private when the input is private. This is not a font validator,
shaping test, kerning review, interpolation test or visual score.

Recovery 2026-10-27: current project documents name Oron 0.935, not Tirgul Seven.
Source and both current static outputs recovered privately; release checksums must
be checked before review. Existing owner feedback names פ, ק and numerals as open.
The width-formula lead has not been established as a current defect.

Reproduction is blocked here by unavailable licensed Ploni/Polin local reference
fonts and build dependencies. The current builder remeasures those references;
do not fabricate measurements or rebuild through its older entrypoint. Obtain a
verified build in the existing authorized environment, then tackle one glyph task.

No font geometry changed in this batch. No before/after improvement, peer approval,
or 10/10 score is claimed. Pending Claude handoff must name exact source/font hashes.
Technical execution in this environment is Linux Python; the Mac Python versions
required by AGENTS.md remain pending and are not claimed as tested.

Reusing prior work: the source status preserves failed optical-thinning trials and
unproven hinting improvements. Do not repeat those as a demonstrated fix.
