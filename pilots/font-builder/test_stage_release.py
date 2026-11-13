"""Release-staging failure controls using generated test fixtures, never designs."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from stage_release import stage


class StageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pins = {}
        for weight in ('Regular', 'Bold'):
            fb = FontBuilder(1000, isTTF=True)
            fb.setupGlyphOrder(['.notdef', 'space'])
            fb.setupCharacterMap({32: 'space'})
            fb.setupGlyf({n: TTGlyphPen(None).glyph() for n in ('.notdef', 'space')})
            fb.setupHorizontalMetrics({n: (500, 0) for n in ('.notdef', 'space')})
            fb.setupHorizontalHeader(ascent=800, descent=-200)
            fb.setupNameTable({'familyName': 'Oron', 'styleName': weight,
                              'uniqueFontIdentifier': 'Oron-0.936-' + weight,
                              'fullName': 'Oron ' + weight,
                              'psName': 'Oron-' + weight, 'version': 'Version 0.936'})
            fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
            fb.setupPost()
            fb.setupMaxp()
            fb.font['head'].fontRevision = .936
            name = 'Oron-0.936-' + weight + '.ttf'
            fb.save(self.root / name)
            self.pins[name] = hashlib.sha256((self.root / name).read_bytes()).hexdigest()
        self.manifest = self.root / 'pins.json'
        self.save_pins()
        self.output = self.root / 'staged'

    def save_pins(self):
        self.manifest.write_text(json.dumps(self.pins))

    def run_stage(self):
        return stage(self.root, self.manifest, '0.936', self.output)

    def test_exact_bytes_and_readback(self):
        report = self.run_stage()
        self.assertFalse(report['installed'])
        for weight in ('Regular', 'Bold'):
            self.assertEqual((self.output / ('Oron-' + weight + '.ttf')).read_bytes(),
                             (self.root / ('Oron-0.936-' + weight + '.ttf')).read_bytes())
        self.assertEqual(json.loads((self.output / 'staged-release.json').read_text()), report)

    def test_corrupt_bold_pin_leaves_no_partial_regular(self):
        self.pins['Oron-0.936-Bold.ttf'] = '0' * 64
        self.save_pins()
        with self.assertRaisesRegex(ValueError, 'Manifest mismatch'):
            self.run_stage()
        self.assertFalse(self.output.exists())

    def test_existing_directory_is_preserved(self):
        self.output.mkdir()
        sentinel = self.output / 'keep'
        sentinel.write_text('canonical')
        with self.assertRaises(ValueError):
            self.run_stage()
        self.assertEqual(sentinel.read_text(), 'canonical')

    def test_stale_alias_renamed_as_versioned_input_is_rejected(self):
        from fontTools.ttLib import TTFont
        path = self.root / 'Oron-0.936-Regular.ttf'
        with TTFont(path) as f:
            for rec in f['name'].names:
                if rec.nameID == 5:
                    rec.string = 'Version 0.935'.encode(rec.getEncoding())
            f.save(path)
        self.pins[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.save_pins()
        with self.assertRaisesRegex(ValueError, 'Name/version mismatch'):
            self.run_stage()
        self.assertFalse(self.output.exists())

    def test_missing_weight_produces_no_output(self):
        (self.root / 'Oron-0.936-Bold.ttf').unlink()
        with self.assertRaises(FileNotFoundError):
            self.run_stage()
        self.assertFalse(self.output.exists())

    def test_output_cannot_equal_source(self):
        self.output = self.root
        with self.assertRaises(ValueError):
            self.run_stage()
        self.assertTrue(self.manifest.exists())


if __name__ == '__main__':
    unittest.main()
