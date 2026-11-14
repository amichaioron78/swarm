"""Verify private source-derived records against actual existing font geometry.

Records must come from the existing source pipeline; this command does not recover
source from font outlines, rebuild a release, verify hinting or assign design scores.
"""
import argparse
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont
from reconstruction_guard import verify_geometry
from trial_glyph import compile_records


def verify(font_path, records_path, required):
    font_path, records_path = Path(font_path), Path(records_path)
    bundle = json.loads(records_path.read_text())
    records = bundle['components']
    names = [item['glyph'] for item in records]
    if len(names) != len(set(names)) or set(names) != set(required):
        raise ValueError('Require exactly the requested glyphs, without duplicates')
    checks = {}
    with TTFont(font_path) as font:
        for item in records:
            name = item['glyph']
            if name not in font['glyf']:
                raise ValueError('Missing font glyph: ' + name)
            rebuilt = compile_records(item)
            shift = item.get('integer_shift', 0)
            if type(shift) is not int:
                raise ValueError('Post-quantization shift must be an integer')
            if shift:
                rebuilt.coordinates.translate((shift, 0))
            checks[name] = verify_geometry(font['glyf'][name], rebuilt, font['glyf'])
    return {'font_sha256': hashlib.sha256(font_path.read_bytes()).hexdigest(),
            'records_sha256': hashlib.sha256(records_path.read_bytes()).hexdigest(),
            'components': checks, 'geometry_matches': len(checks),
            'scope': 'geometry only; full release/hints/metrics/visual approval unverified'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('font', type=Path)
    p.add_argument('records', type=Path)
    p.add_argument('--require', nargs='+', required=True)
    args = p.parse_args()
    print(json.dumps(verify(args.font, args.records, args.require), indent=2))
