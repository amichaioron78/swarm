"""Independent lifecycle review: conservation, failure atomicity and history."""
import copy
import random
import unittest
from datetime import datetime, timedelta, timezone

from swarm import Room


class RoundReviewTests(unittest.TestCase):
    def room(self, contribution=100):
        r = Room(contribution=contribution)
        now = datetime(2026, 11, 16, tzinfo=timezone.utc)
        r.join('alpha', 'mock', 'A', now)
        r.join('beta', 'mock', 'B', now)
        return r, now

    def test_conservation_over_many_rounds_and_new_contributions(self):
        rng = random.Random(16112026)
        for contribution in (1, 3, 7, 100):
            r, now = self.room(contribution)
            for n in range(25):
                if n:
                    r.join('new-%d' % n, 'mock', 'A' if n % 2 else 'B', now)
                (r.start if n == 0 else r.next_round)()
                for bucket, balance in list(r.balances.items()):
                    units = rng.randint(0, balance)
                    if units:
                        r.debit(bucket, units)
                    self.assertEqual(r.pool, r.spent + sum(r.balances.values()) + r.available())
                snapshot = r.end_round()
                self.assertEqual(sum(snapshot['allocated'].values()),
                                 snapshot['spent'] + sum(snapshot['unspent'].values()))
                self.assertEqual(r.available(), r.pool - r.spent)
            self.assertEqual(sum(x['spent'] for x in r.rounds.values()), r.spent)

    def test_failed_transitions_are_atomic(self):
        r, now = self.room()
        r.start()
        for operation in (r.start, r.next_round, lambda: r.join('extra', 'mock', 'A', now),
                          lambda: r.debit('A', 81)):
            before = copy.deepcopy(r.__dict__)
            with self.assertRaises(ValueError):
                operation()
            self.assertEqual(r.__dict__, before)
        r.end_round()
        r.leave('beta', now)
        before = copy.deepcopy(r.__dict__)
        with self.assertRaises(ValueError):
            r.next_round()
        self.assertEqual(r.__dict__, before)

    def test_returned_history_is_detached_and_survives_team_change(self):
        r, now = self.room()
        r.start()
        r.record_verified_outcome('first', 'A', .75, {'alpha': 1})
        r.leave('alpha', now)
        original = r.end_round()
        changed = r.round_summary(1)
        for key in ('members', 'allocated', 'unspent'):
            changed[key].clear()
        changed['results'].clear()
        r.join('alpha', 'mock', 'B', now + timedelta(days=183))
        r.join('replacement', 'mock', 'A', now + timedelta(days=183))
        r.next_round()
        r.record_verified_outcome('second', 'B', .5, {'alpha': 1})
        self.assertEqual(r.round_summary(1), original)
        self.assertEqual(r.scoreboard(1)['individuals'], {'alpha': 75})
        self.assertEqual(r.scoreboard(1)['teams'], {'A': 75, 'B': 0})
        self.assertEqual(r.scoreboard()['individuals']['alpha'], 125)

    def test_exhausted_pool_cannot_be_spent_again(self):
        r, _ = self.room()
        r.start()
        for bucket, units in list(r.balances.items()):
            r.debit(bucket, units)
        r.end_round()
        r.next_round()
        self.assertEqual(sum(r.balances.values()), 0)
        with self.assertRaises(ValueError):
            r.debit('A', 1)
        self.assertEqual(r.spent, r.pool)
