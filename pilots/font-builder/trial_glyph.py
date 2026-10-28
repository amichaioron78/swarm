"""Compile a single-glyph trial into a COPY of an existing unhinted TrueType font.

Require exact baseline reconstruction before accepting candidate records.
This is a private review prototype, not a substitute for the full source build.
Input record JSON: glyph, records (RecordingPen commands), x_offset.
Requires fonttools. No reference font or source is embedded here.
"""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen


def compile_records(data):
    pen = TTGlyphPen(None)
    transformed = TransformPen(Cu2QuPen(pen, .5, reverse_direction=False),
                               (1, 0, 0, 1, data['x_offset'], 0))
    allowed = {'moveTo', 'lineTo', 'curveTo', 'qCurveTo', 'closePath'}
    for op, points in data['records']:
        if op not in allowed:
            raise ValueError('Unsupported outline command: ' + str(op))
        args = [tuple(p) if p is not None else None for p in points]
        getattr(transformed, op)(*args)
    return pen.glyph()


def make_trial(baseline, old_data, new_data, output):
    baseline, output = Path(baseline), Path(output)
    if output.exists() or output.resolve() == baseline.resolve():
        raise ValueError('Output must be new; baseline cannot be overwritten')
    name = old_data['glyph']
    if new_data['glyph'] != name:
        raise ValueError('Baseline and candidate must target the same glyph')
    font = TTFont(baseline, recalcTimestamp=False)
    glyf = font['glyf']
    if name not in glyf:
        raise ValueError('Target glyph is absent')
    original = {n: glyf[n].compile(glyf) for n in font.getGlyphOrder()}
    if compile_records(old_data).compile(glyf) != original[name]:
        raise ValueError('Reconstruction does not exactly match the baseline glyph')
    metrics = dict(font['hmtx'].metrics)
    glyf[name] = compile_records(new_data)
    if glyf[name].compile(glyf) == original[name]:
        raise ValueError('Candidate does not change the target')
    font.save(output)
    font.close()
    check = TTFont(output)
    changed = [n for n in check.getGlyphOrder()
               if check['glyf'][n].compile(check['glyf']) != original[n]]
    if changed != [name] or check['hmtx'].metrics != metrics:
        output.unlink()
        raise ValueError('Unexpected outline or metric changes; trial removed')
    check.close()
    return {'baseline_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
            'candidate_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'exact_source_reconstruction': True, 'changed_glyphs': changed,
            'horizontal_metrics_unchanged': True,
            'status': 'unhinted review prototype; full build and visual approval pending'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('baseline', 'old_records', 'new_records', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(make_trial(args.baseline, json.loads(args.old_records.read_text()),
                               json.loads(args.new_records.read_text()), args.output), indent=2))
