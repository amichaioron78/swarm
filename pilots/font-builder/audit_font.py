"""Read-only audit of an existing font. No visual score or reference substitution.

Requires fonttools. Prints JSON; never writes or changes the input font.
Usage: python audit_font.py existing.ttf [--candidate candidate.ttf]
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen

LETTERS = ''.join(chr(c) for c in range(0x5D0, 0x5EB))
REQUIRED = LETTERS + '0123456789 .,!?-:;()'


def audit(path):
    raw = Path(path).read_bytes()
    font = TTFont(io.BytesIO(raw), checkChecksums=2)
    # Force decoding every table; a lazy TTFont open alone proves little.
    for tag in font.keys():
        font[tag]
    cmap = font.getBestCmap() or {}
    gs = font.getGlyphSet()
    glyphs = {}
    for ch in REQUIRED:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        pen = BoundsPen(gs)
        gs[name].draw(pen)
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        advance, lsb = font['hmtx'][name]
        glyphs[ch] = {
            'glyph': name, 'advance': advance, 'lsb': lsb,
            'rsb': advance - pen.bounds[2] if pen.bounds else None,
            'bounds': pen.bounds,
            'outline_sha256': hashlib.sha256(repr(rec.value).encode()).hexdigest(),
        }
    result = {
        'format': 'font-pilot-audit/1',
        'sha256': hashlib.sha256(raw).hexdigest(),
        'font_revision': font['head'].fontRevision,
        'units_per_em': font['head'].unitsPerEm,
        'glyph_count': len(font.getGlyphOrder()),
        'missing_required': [ch for ch in REQUIRED if ord(ch) not in cmap],
        'niqqud_present': [f'U+{c:04X}' for c in range(0x5B0, 0x5BE) if c in cmap],
        'variable_axes': [a.axisTag for a in font['fvar'].axes] if 'fvar' in font else [],
        'layout_tables': [t for t in ('GPOS', 'GSUB', 'kern') if t in font],
        'glyphs': glyphs,
        'visual_quality': 'unassessed; technical results are not design acceptance',
    }
    font.close()
    return result


def compare(before, after):
    a, b = before['glyphs'], after['glyphs']
    return {
        'baseline_sha256': before['sha256'], 'candidate_sha256': after['sha256'],
        'changed_glyphs': [ch for ch in sorted(set(a) | set(b)) if a.get(ch) != b.get(ch)],
        'warning': 'Glyph/metric comparison only; layout tables and raster behavior require separate checks.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('--candidate', type=Path)
    args = parser.parse_args()
    before = audit(args.baseline)
    result = {'baseline': before}
    if args.candidate:
        after = audit(args.candidate)
        result.update(candidate=after, comparison=compare(before, after))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
