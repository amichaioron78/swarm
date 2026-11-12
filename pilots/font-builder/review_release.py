"""Read-only matched release specimen and hint-inventory report.

Inputs stay private; output contains private outlines rendered as PNG. Requires
fonttools and Pillow with RAQM. No typography score or release approval.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features
from fontTools.ttLib import TTFont
from compare_release import compare

SIZES = (12, 16, 24, 48, 96)
SAMPLES = ('פף ממ מפה מספרים 0123456789',
           'אבגדהוזחטיכלמנסעפצקרשת ךםןףץ',
           '0123456789', 'מפה פתוחה, מספר חדש: 2026.')


def hint_inventory(path):
    with TTFont(path) as font:
        result = {}
        for name in font.getGlyphOrder():
            program = getattr(font['glyf'][name], 'program', None)
            result[name] = len(program.getBytecode()) if program else 0
        return result


def review(before, after, allowed, output):
    if not features.check('raqm'):
        raise RuntimeError('RAQM is required; do not substitute pre-reversed text')
    output = Path(output)
    if output.exists():
        raise ValueError('Output directory must be new')
    # Confirm text coverage before rasterizing, so tofu/fallback cannot pass silently.
    for path in (before, after):
        with TTFont(path) as font:
            missing = set(''.join(SAMPLES)) - {chr(c) for c in font.getBestCmap()}
            if missing:
                raise ValueError('Missing specimen characters: ' + repr(missing))
    report = compare(before, after, allowed)
    old, new = hint_inventory(before), hint_inventory(after)
    report['lost_glyph_instructions'] = [n for n in old if old[n] and not new.get(n)]
    report['hint_byte_lengths'] = {'baseline': old, 'candidate': new}
    report['render'] = {'sizes_ppem': SIZES, 'engine': 'Pillow RAQM',
                        'samples': SAMPLES, 'benchmark': 'unavailable; no substitution'}
    rows = []
    width = 1200
    for size in SIZES:
        for label, path in (('Baseline', before), ('Release', after)):
            font = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)
            heights = []
            for sample in SAMPLES:
                box = font.getbbox(sample, direction='rtl')
                width = max(width, box[2] - box[0] + 280)
                heights.append(max(size + 12, box[3] - box[1] + 18))
            rows.append((label, size, font, heights))
    canvas = Image.new('RGB', (width, sum(sum(r[3]) + 36 for r in rows) + 50), 'white')
    draw = ImageDraw.Draw(canvas)
    ui = ImageFont.truetype('DejaVuSans.ttf', 17)
    draw.text((20, 12), 'Actual font comparison | native ppem | no benchmark or design score', font=ui, fill='black')
    y = 45
    for label, size, font, heights in rows:
        draw.text((20, y), f'{label} / {size} ppem', font=ui, fill='black')
        y += 30
        for sample, height in zip(SAMPLES, heights):
            draw.text((width - 24, y), sample, font=font, fill='black', anchor='rt', direction='rtl')
            y += height
        draw.line((20, y, width - 20, y), fill='#dddddd')
        y += 6
    output.mkdir(parents=True)
    canvas.save(output / 'before-after.png')
    report['specimen_sha256'] = hashlib.sha256((output / 'before-after.png').read_bytes()).hexdigest()
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--allow', nargs='+', required=True)
    args = parser.parse_args()
    result = review(args.before, args.after, args.allow, args.output)
    print(json.dumps({k: result[k] for k in ('changed_outlines', 'blockers', 'lost_glyph_instructions')}, indent=2))
    raise SystemExit(bool(result['blockers']))
