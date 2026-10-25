import unittest
from datetime import datetime, timedelta, timezone
from swarm import Room


class SwarmTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 25, tzinfo=timezone.utc)
        self.r = Room()
        self.r.join('one', 'mock-x', 'A', self.now)
        self.r.join('two', 'mock-y', 'B', self.now)

    def test_requires_two_teams(self):
        r = Room()
        r.join('solo', 'mock-x', 'A', self.now)
        with self.assertRaises(ValueError): r.start()

    def test_equal_budgets_despite_unequal_team_sizes(self):
        self.r.join('three', 'mock-z', 'A', self.now)
        self.r.start()
        self.assertEqual(self.r.balances, {'A': 120, 'B': 120, 'referee': 60})

    def test_overspend_does_not_change_ledger(self):
        self.r.start()
        with self.assertRaises(ValueError): self.r.debit('A', 81)
        self.assertEqual(self.r.spent, 0)
        self.assertEqual(self.r.balances['A'], 80)

    def test_invalid_spend_rejected(self):
        self.r.start()
        for value in [-1, 0, 1.5, True]:
            with self.assertRaises(ValueError): self.r.debit('A', value)

    def test_score_not_spendable_and_duplicate_outcome_blocked(self):
        self.r.start()
        self.r.record_verified_outcome('win', 'A', .8, {'one': 1})
        with self.assertRaises(ValueError): self.r.record_verified_outcome('win', 'A', .8, {'one': 1})
        self.assertEqual(self.r.points['one'], 80)
        self.assertEqual(self.r.balances['A'], 80)

    def test_invalid_scores_leave_no_result(self):
        self.r.start()
        for value in [float('nan'), float('inf'), -1, 2, True]:
            with self.assertRaises(ValueError): self.r.record_verified_outcome('bad', 'A', value, {'one': 1})
        self.assertEqual(self.r.results, {})

    def test_cannot_award_other_team(self):
        self.r.start()
        with self.assertRaises(ValueError): self.r.record_verified_outcome('bad', 'A', 1, {'two': 1})

    def test_credit_split(self):
        self.r.join('three', 'mock-z', 'A', self.now)
        self.r.start()
        self.r.record_verified_outcome('win', 'A', 1, {'one': .3, 'three': .7})
        self.assertEqual(self.r.points['one'], 30)
        self.assertEqual(self.r.points['three'], 70)

    def test_leave_revokes_notes_and_locks_reentry(self):
        self.r.leave('one', self.now)
        with self.assertRaises(ValueError): self.r.read_notes('one')
        with self.assertRaises(ValueError): self.r.publish_note('one', 'hello', True)
        with self.assertRaises(ValueError): self.r.join('one', 'mock-x', 'A', self.now + timedelta(days=182))
        self.r.join('one', 'mock-x', 'A', self.now + timedelta(days=183))
        self.assertEqual(self.r.pool, 300)

    def test_join_does_not_allow_multiple_seats_for_owner(self):
        with self.assertRaises(ValueError): self.r.join('one', 'mock-z', 'B', self.now)

    def test_notes_need_approval_and_allow_names(self):
        with self.assertRaises(ValueError): self.r.publish_note('one', 'Bob has a public UX request', False)
        self.r.publish_note('one', 'Bob has a public UX request', True)
        notes = self.r.read_notes('two')
        notes[0]['text'] = 'changed'
        self.assertEqual(self.r.read_notes('two')[0]['text'], 'Bob has a public UX request')

    def test_budget_conservation_and_tie(self):
        self.r.start()
        for bucket in ['A', 'B', 'referee']: self.r.debit(bucket, 10)
        self.assertEqual(sum(self.r.balances.values()) + self.r.spent, self.r.pool)
        self.assertIsNone(self.r.scoreboard()['winner'])


if __name__ == '__main__': unittest.main()
