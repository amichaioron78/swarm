import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.workspace import bundle, digest, read_records, safe_file, search, validate

ROOT = Path(__file__).resolve().parents[1]


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.records = read_records(ROOT)

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
        self.records[2]['summary'] = 'New unsupported claim'
        errors = validate(ROOT, self.records)
        self.assertTrue(any('stale' in e for e in errors))
        self.assertTrue(any('independent review' in e for e in errors))

    def test_self_review_rejected(self):
        self.records[3]['author'] = self.records[2]['author']
        errors = validate(ROOT, self.records)
        self.assertTrue(any('self-review' in e for e in errors))

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
        self.records.append(copy.deepcopy(self.records[0]))
        self.records[0]['links'] = ['not-found']
        errors = validate(ROOT, self.records)
        self.assertTrue(any('duplicate' in e for e in errors))
        self.assertTrue(any('missing linked' in e for e in errors))

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

    def test_digest_ignores_json_key_order(self):
        value = self.records[0]
        self.assertEqual(digest(value), digest(dict(reversed(list(value.items())))))


if __name__ == '__main__':
    unittest.main()
