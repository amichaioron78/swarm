import copy
import base64
import subprocess
import sys
import json
import tempfile
import shutil
import unittest
from pathlib import Path
from tools.workspace import bundle, digest, read_records, safe_file, search, validate

ROOT = Path(__file__).resolve().parents[1]


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.records = read_records(ROOT)

    def rec(self, ident):
        return next(r for r in self.records if r['id'] == ident)

    def test_fixture_is_valid(self):
        self.assertEqual(validate(ROOT, self.records), [])

    def test_failing_experiment_remains_searchable(self):
        results = search(self.records, 'failed')
        self.assertTrue(any(r['id'] == 'experiment-chat-only' for r in results))

    def test_project_filter_does_not_leak_other_records(self):
        self.assertEqual(search(self.records, '', 'another-project'), [])

    def test_second_worker_can_follow_reuse_chain(self):
        by_id = {r['id']: r for r in self.records}
        second = by_id['experiment-second-worker']
        finding = by_id[second['links'][0]]
        self.assertEqual(finding['status'], 'accepted')
        self.assertEqual(by_id[second['based_on']]['status'], 'failed')

    def test_edited_finding_invalidates_review(self):
        self.rec('finding-persistent-record')['summary'] = 'New unsupported claim'
        errors = validate(ROOT, self.records)
        self.assertTrue(any('stale' in e for e in errors))
        self.assertTrue(any('independent review' in e for e in errors))

    def test_self_review_rejected(self):
        self.rec('review-persistent-record')['author'] = self.rec('finding-persistent-record')['author']
        errors = validate(ROOT, self.records)
        self.assertTrue(any('self-review' in e for e in errors))

    def test_author_case_and_whitespace_cannot_bypass_self_review(self):
        self.rec('review-persistent-record')['author'] = '  ' + self.rec('finding-persistent-record')['author'].upper() + '  '
        self.assertTrue(any('self-review' in e for e in validate(ROOT, self.records)))

    def test_planned_experiment_can_precede_evidence(self):
        self.rec('experiment-chat-only')['status'] = 'planned'
        self.rec('experiment-chat-only')['evidence'] = []
        self.assertEqual(validate(ROOT, self.records), [])

    def test_missing_evidence_rejected(self):
        self.records[1]['evidence'] = ['missing.txt']
        self.assertTrue(any('evidence' in e for e in validate(ROOT, self.records)))

    def test_path_escape_rejected(self):
        self.assertIsNone(safe_file(ROOT, '../swarm_bridge/README.md'))
        self.assertIsNone(safe_file(ROOT, '/etc/passwd'))

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'escape').symlink_to('/etc/passwd')
            self.assertIsNone(safe_file(root, 'escape'))

    def test_duplicate_and_missing_link_rejected(self):
        self.records.append(copy.deepcopy(self.rec('experiment-chat-only')))
        self.rec('experiment-chat-only')['links'] = ['not-found']
        errors = validate(ROOT, self.records)
        self.assertTrue(any('duplicate' in e for e in errors))
        self.assertTrue(any('missing linked' in e for e in errors))

    def test_evidence_edit_requires_updated_pin_and_review(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(ROOT/'workspace', root/'workspace')
            (root/'workspace/protocols/pilot-evidence.md').write_text('Different evidence')
            self.assertTrue(any('checksum' in e for e in validate(root, self.records)))

    def test_export_is_json_portable_with_attachments(self):
        exported = json.loads(json.dumps(bundle(ROOT, self.records)))
        self.assertEqual(exported['records'], self.records)
        self.assertIn('workspace/protocols/pilot-evidence.md', exported['files'])
        self.assertIn('workspace/skills/evidence-review/instructions.md', exported['files'])

    def test_skill_needs_actual_instructions(self):
        next(r for r in self.records if r['kind'] == 'skill')['instructions'] = '../outside'
        self.assertTrue(any('instructions' in e for e in validate(ROOT, self.records)))

    def test_non_object_file_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'workspace'/'records'
            target.mkdir(parents=True)
            (target/'bad.json').write_text('[]')
            with self.assertRaises(ValueError):
                read_records(Path(folder))

    def test_malformed_kind_and_status_return_errors(self):
        for field in ('kind', 'status'):
            for value in ([], {}, None, 1):
                with self.subTest(field=field, value=value):
                    records = read_records(ROOT)
                    records[0][field] = value
                    self.assertTrue(validate(ROOT, records))

    def test_lifecycle_change_keeps_substantive_review_valid(self):
        finding = self.rec('finding-persistent-record')
        original = digest(finding)
        finding['status'] = 'proposed'
        self.assertEqual(digest(finding), original)
        finding['status'] = 'accepted'
        self.assertEqual(validate(ROOT, self.records), [])

    def test_blocking_review_prevents_acceptance(self):
        blocker = copy.deepcopy(self.rec('review-persistent-record'))
        blocker.update(id='review-blocker', author='another-reviewer', status='changes_requested')
        self.records.append(blocker)
        self.assertTrue(any('blocking' in e for e in validate(ROOT, self.records)))

    def test_export_preserves_binary_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'evidence.bin').write_bytes(b'\x89PNG\xff')
            exported = bundle(root, [{'evidence': ['evidence.bin']}])
            item = exported['files']['evidence.bin']
            self.assertEqual(base64.b64decode(item['content']), b'\x89PNG\xff')

    def test_empty_review_check_rejected(self):
        self.rec('review-persistent-record')['checks'] = ['']
        self.assertTrue(any('checks' in e for e in validate(ROOT, self.records)))

    def test_search_does_not_match_property_names(self):
        self.assertEqual(search(self.records, 'schema_version'), [])

    def test_invalid_record_does_not_block_read_only_search(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(ROOT/'workspace', root/'workspace')
            target = root/'workspace/records/finding-persistent-record.json'
            value = json.loads(target.read_text())
            value['summary'] = 'Changed unreviewed claim'
            target.write_text(json.dumps(value))
            result = subprocess.run([sys.executable, str(ROOT/'tools/workspace.py'),
                                     '--root', str(root), 'search', 'failed'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('WARNING', result.stderr)
            self.assertTrue(json.loads(result.stdout))

    def test_bad_json_names_the_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)/'workspace'/'records'
            target.mkdir(parents=True)
            (target/'broken.json').write_text('{bad')
            with self.assertRaisesRegex(ValueError, 'broken.json'):
                read_records(Path(folder))

    def test_digest_ignores_json_key_order(self):
        value = self.rec('experiment-chat-only')
        self.assertEqual(digest(value), digest(dict(reversed(list(value.items())))))


if __name__ == '__main__':
    unittest.main()
