"""Portable Swarm records. Python 3.9+, standard library only.

This validates public example records; it is not an authorization service.
"""
from __future__ import annotations

import argparse
import base64
import sys
import hashlib
import json
import re
from pathlib import Path

KINDS = {
    'task': {'open', 'doing', 'review', 'done', 'cancelled'},
    'finding': {'proposed', 'accepted', 'rejected', 'superseded'},
    'experiment': {'planned', 'running', 'succeeded', 'failed', 'inconclusive'},
    'review': {'approved', 'changes_requested', 'comment'},
    'skill': {'draft', 'released', 'deprecated'},
}


def digest(record):
    """Pin substantive content; lifecycle status can change after review."""
    content = {key: value for key, value in record.items() if key != 'status'}
    return hashlib.sha256(json.dumps(content, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


def actor(value):
    return value.strip().casefold() if isinstance(value, str) else ''


def read_records(root):
    records = []
    for path in sorted((root / 'workspace' / 'records').glob('*.json')):
        try:
            value = json.loads(path.read_text(encoding='utf-8'))
        except ValueError as exc:
            raise ValueError('%s: %s' % (path, exc)) from exc
        if not isinstance(value, dict):
            raise ValueError('%s must contain a JSON object' % path)
        records.append(value)
    return records


def safe_file(root, relative):
    if not isinstance(relative, str) or not relative:
        return None
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def validate(root, records):
    errors = []
    ids = {}
    for r in records:
        ident = r.get('id')
        if not isinstance(ident, str) or not re.fullmatch(r'[a-z][a-z0-9_-]*', ident):
            errors.append('invalid id: %r' % ident)
            continue
        if ident in ids:
            errors.append('duplicate id: ' + ident)
        ids[ident] = r
    for r in records:
        ident = r.get('id', '?')
        def fail(message):
            errors.append('%s: %s' % (ident, message))
        if r.get('schema_version') != 1:
            fail('schema_version must be 1')
        for field in ('title', 'author', 'owner', 'project', 'summary'):
            if not isinstance(r.get(field), str) or not r[field].strip():
                fail(field + ' must be nonempty text')
        if r.get('visibility') != 'public':
            fail('this public repository accepts public records only')
        kind = r.get('kind')
        status = r.get('status')
        if not isinstance(kind, str) or kind not in KINDS:
            fail('invalid kind/status')
            kind = None
        elif not isinstance(status, str) or status not in KINDS[kind]:
            fail('invalid kind/status')
        links = r.get('links')
        if not isinstance(links, list) or any(not isinstance(x, str) for x in links):
            fail('links must be a list of record IDs')
            links = []
        for link in links:
            if link not in ids:
                fail('missing linked record ' + link)
        if 'based_on' in r and (not isinstance(r['based_on'], str) or r['based_on'] not in ids):
            fail('missing parent branch record')
        if kind in {'finding', 'experiment'}:
            needs_evidence = kind == 'finding' or r.get('status') in ('succeeded', 'failed', 'inconclusive')
            if not isinstance(r.get('evidence'), list) or (needs_evidence and not r['evidence']):
                fail('evidence is required, including for failed experiments')
            else:
                for evidence in r['evidence']:
                    path = safe_file(root, evidence)
                    if path is None:
                        fail('evidence must name an existing repository file')
                    else:
                        pins = r.get('evidence_sha256')
                        actual = hashlib.sha256(path.read_bytes()).hexdigest()
                        if not isinstance(pins, dict) or pins.get(evidence) != actual:
                            fail('evidence checksum missing or changed; revise and review again')
        if kind == 'finding' and r.get('status') == 'accepted':
            if not any(review.get('kind') == 'review'
                       and review.get('status') == 'approved'
                       and review.get('target') == ident
                       and review.get('target_sha256') == digest(r)
                       and actor(review.get('author')) != actor(r.get('author')) for review in records):
                fail('accepted finding needs independent review of this exact content')
        if kind == 'finding' and r.get('status') == 'accepted':
            if any(review.get('kind') == 'review'
                   and review.get('status') == 'changes_requested'
                   and review.get('target') == ident
                   and review.get('target_sha256') == digest(r) for review in records):
                fail('accepted finding has an unresolved blocking review')
        if kind == 'review':
            target = ids.get(r.get('target')) if isinstance(r.get('target'), str) else None
            if not target:
                fail('review target is missing')
            elif target.get('kind') == 'review':
                fail('review target must be a work record, not another review')
            else:
                if actor(r.get('author')) == actor(target.get('author')):
                    fail('self-review cannot supply independent approval')
                if r.get('target_sha256') != digest(target):
                    fail('review is stale: target content changed')
            if (not isinstance(r.get('checks'), list) or not r['checks']
                    or any(not isinstance(check, str) or not check.strip() for check in r['checks'])):
                fail('review must state checks performed')
        if kind == 'skill':
            if not isinstance(r.get('version'), str) or not re.fullmatch(r'\d+\.\d+\.\d+', r['version']):
                fail('skill needs a semantic version')
            if not safe_file(root, r.get('instructions')):
                fail('skill instructions must exist inside repository')
            if not isinstance(r.get('permissions'), list):
                fail('skill must declare required permissions')
    return errors


def values(value):
    if isinstance(value, dict):
        return ' '.join(values(v) for v in value.values())
    if isinstance(value, list):
        return ' '.join(values(v) for v in value)
    return str(value)


def search(records, query, project=None):
    terms = query.casefold().split()
    return [r for r in records if (not project or r.get('project') == project)
            and all(t in values(r).casefold() for t in terms)]


def bundle(root, records):
    """Self-contained JSON export of records and their text attachments."""
    files = {}
    for r in records:
        paths = list(r.get('evidence', []))
        if r.get('instructions'):
            paths.append(r['instructions'])
        for relative in paths:
            path = safe_file(root, relative)
            if path:
                raw = path.read_bytes()
                try:
                    files[relative] = raw.decode('utf-8')
                except UnicodeDecodeError:
                    files[relative] = {'encoding': 'base64',
                                       'content': base64.b64encode(raw).decode('ascii'),
                                       'sha256': hashlib.sha256(raw).hexdigest(),
                                       'size_bytes': len(raw)}
    return {'format': 'swarm-workspace/1', 'records': records, 'files': files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    query = sub.add_parser('search')
    query.add_argument('query')
    query.add_argument('--project')
    sub.add_parser('export')
    sub.add_parser('skills')
    show = sub.add_parser('show')
    show.add_argument('id')
    pin = sub.add_parser('digest')
    pin.add_argument('id')
    args = parser.parse_args()
    try:
        records = read_records(args.root)
        if args.command == 'digest':
            target = next((r for r in records if r.get('id') == args.id), None)
            if target is None:
                raise ValueError('unknown record: ' + args.id)
            print(digest(target))
            return
        errors = validate(args.root, records)
        if errors and args.command == 'validate':
            raise ValueError('\n'.join(errors))
        if errors:
            print('WARNING: unvalidated records; do not treat acceptance as verified:\n' + '\n'.join(errors), file=sys.stderr)
        if args.command == 'validate':
            print('Valid: %d records' % len(records))
        elif args.command == 'search':
            print(json.dumps(search(records, args.query, args.project), indent=2))
        elif args.command == 'skills':
            print(json.dumps([r for r in records if r['kind'] == 'skill'], indent=2))
        elif args.command == 'export':
            print(json.dumps(bundle(args.root, records), indent=2))
        else:
            record = next((r for r in records if r['id'] == args.id), None)
            if record is None:
                raise ValueError('unknown record: ' + args.id)
            print(digest(record) if args.command == 'digest' else json.dumps(record, indent=2))
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
