"""Read-only release isolation check on two actual TrueType/OpenType fonts.

Usage: python compare_release.py baseline.ttf candidate.ttf --allow pe finalpe
Requires fonttools. No reference fonts, model calls or automatic quality score.
"""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

PROTECTED = ('cmap', 'hmtx', 'vmtx', 'GPOS', 'GSUB', 'GDEF', 'kern',
             'fpgm', 'prep', 'cvt ', 'gasp', 'OS/2', 'hhea')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def outline(font, name):
    gs = font.getGlyphSet()
    pen = DecomposingRecordingPen(gs)
    gs[name].draw(pen)
    return pen.value


def compare(baseline, candidate, allowed):
    with TTFont(baseline, recalcTimestamp=False) as a, TTFont(candidate, recalcTimestamp=False) as b:
        order_a, order_b = a.getGlyphOrder(), b.getGlyphOrder()
        names = sorted(set(order_a) | set(order_b))
        changed = [n for n in names if n not in order_a or n not in order_b
                   or outline(a, n) != outline(b, n)]
        protected = {}
        for tag in PROTECTED:
            left = a.getTableData(tag) if tag in a else None
            right = b.getTableData(tag) if tag in b else None
            protected[tag] = {'equal': left == right,
                              'baseline_sha256': sha(left) if left is not None else None,
                              'candidate_sha256': sha(right) if right is not None else None}
        hints = []
        if 'glyf' in a and 'glyf' in b:
            for n in sorted(set(order_a) & set(order_b)):
                pa = getattr(a['glyf'][n], 'program', None)
                pb = getattr(b['glyf'][n], 'program', None)
                if (pa.getBytecode() if pa else b'') != (pb.getBytecode() if pb else b''):
                    hints.append(n)
        blockers = []
        if order_a != order_b:
            blockers.append('Glyph order/coverage differs')
        if set(allowed) - set(order_a):
            blockers.append('Allowed glyph name absent from baseline')
        if set(changed) - set(allowed):
            blockers.append('Unexpected outline changes')
        if not changed:
            blockers.append('Candidate contains no outline change')
        if any(not value['equal'] for value in protected.values()):
            blockers.append('Protected coverage/metrics/layout table changed')
        return {'format': 'font-release-diff/1',
                'baseline_sha256': sha(Path(baseline).read_bytes()),
                'candidate_sha256': sha(Path(candidate).read_bytes()),
                'allowed_glyphs': sorted(allowed), 'changed_outlines': changed,
                'glyph_count': [len(order_a), len(order_b)],
                'glyph_order_equal': order_a == order_b,
                'protected_tables': protected, 'changed_glyph_instructions': hints,
                'blockers': blockers,
                'scope': 'Isolation check only. Hint/global program effects, rasterization, visual quality and owner acceptance need separate review.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--allow', nargs='+', required=True)
    args = parser.parse_args()
    result = compare(args.baseline, args.candidate, args.allow)
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['blockers']))
