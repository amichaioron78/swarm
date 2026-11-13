"""Stage existing Oron exports under default filenames, without installing them.

Pinned hashes identify approved input bytes, not visual approval or reproducibility.
Requires fonttools. Never rewrites font tables or a canonical output directory.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont


def stage(source, manifest, version, output):
    source, output = Path(source), Path(output)
    if not re.fullmatch(r'\d+\.\d{3}', version):
        raise ValueError('Expected explicit version such as 0.936')
    if output.exists() or output.is_symlink():
        raise ValueError('Output must be a new isolated directory')
    pins = json.loads(Path(manifest).read_text())
    payloads, records = {}, {}
    # Validate BOTH inputs before creating any output. Keep validated bytes in memory
    # so a later source replacement cannot alter the staged file.
    for weight in ('Regular', 'Bold'):
        name = 'Oron-{}-{}.ttf'.format(version, weight)
        path = source / name
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if pins.get(name) != digest:
            raise ValueError('Manifest mismatch: ' + name)
        from io import BytesIO
        with TTFont(BytesIO(data), checkChecksums=2) as font:
            for table in font.keys():
                if table != 'GlyphOrder':
                    font[table]  # force all tables to decode before staging
            names = font['name']
            expected = {1: 'Oron', 2: weight, 3: 'Oron-{}-{}'.format(version, weight),
                        5: 'Version ' + version, 6: 'Oron-' + weight}
            if any(names.getDebugName(k) != v for k, v in expected.items()):
                raise ValueError('Name/version mismatch: ' + name)
            if abs(font['head'].fontRevision - float(version)) > 1 / 65536:
                raise ValueError('Head version mismatch: ' + name)
        alias = 'Oron-' + weight + '.ttf'
        payloads[alias] = data
        records[alias] = {'source': name, 'sha256': digest}
    # mkdir(exist_ok=False) arbitrates concurrent attempts. Clean up only a directory
    # this invocation created; an existing canonical tree is never removed.
    output.mkdir()
    try:
        for alias, data in payloads.items():
            with (output / alias).open('xb') as handle:
                handle.write(data)
            if hashlib.sha256((output / alias).read_bytes()).hexdigest() != records[alias]['sha256']:
                raise OSError('Staged readback mismatch')
        report = {'version': version, 'files': records, 'installed': False,
                  'approval': 'pending peer/owner release review; no design score'}
        (output / 'staged-release.json').write_text(json.dumps(report, indent=2) + '\n')
    except BaseException:
        shutil.rmtree(output)
        raise
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('version')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(stage(args.source, args.manifest, args.version, args.output), indent=2))
