"""Compile an isolated unhinted component trial from private source records.

Require exact baseline geometry, keep integer centering after quantization,
and check all other outlines and horizontal metrics after serialization.
Both control and trial strip glyph hints; these are visual review copies only.
"""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.ttProgram import Program
from reconstruction_guard import verify_geometry
from trial_glyph import compile_records


def component(data):
    g = compile_records(data)
    shift = data.get('integer_shift', 0)
    if type(shift) is not int:
        raise ValueError('Post-quantization shift must be an integer')
    g.coordinates.translate((shift, 0))
    return g


def make_trial(baseline, old, new, destination):
    baseline, destination = Path(baseline), Path(destination)
    if destination.exists():
        raise ValueError('Destination must be new')
    if old['glyph'] != new['glyph']:
        raise ValueError('Target glyph mismatch')
    name = old['glyph']
    with TTFont(baseline, recalcTimestamp=False) as f:
        verify_geometry(f['glyf'][name], component(old), f['glyf'])
        candidate = component(new)
        a = f['glyf'][name].getCoordinates(f['glyf'])
        b = candidate.getCoordinates(f['glyf'])
        if all(list(x) == list(y) for x, y in zip(a, b)):
            raise ValueError('Candidate must change geometry')
        destination.mkdir(parents=True)
        for g in f['glyf'].glyphs.values():
            g.expand(f['glyf'])
            g.program = Program()
        original = {n: f['glyf'][n].compile(f['glyf']) for n in f.getGlyphOrder()}
        metrics = dict(f['hmtx'].metrics)
        f.save(destination/'control.ttf')
        f['glyf'][name] = candidate
        f.save(destination/'candidate.ttf')
    with TTFont(destination/'candidate.ttf') as check:
        changed = [n for n in check.getGlyphOrder()
                   if check['glyf'][n].compile(check['glyf']) != original[n]]
        if changed != [name] or check['hmtx'].metrics != metrics:
            raise ValueError('Isolation failed; retain files for diagnosis only')
    return {'changed_glyphs': changed, 'horizontal_metrics_unchanged': True,
            'baseline_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest(),
            'outputs': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in destination.glob('*.ttf')},
            'scope': 'unhinted isolated prototype; full build and visual approval pending'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('baseline', 'old_records', 'new_records', 'destination'):
        p.add_argument(arg, type=Path)
    a = p.parse_args()
    print(json.dumps(make_trial(a.baseline, json.loads(a.old_records.read_text()),
                               json.loads(a.new_records.read_text()), a.destination), indent=2))
