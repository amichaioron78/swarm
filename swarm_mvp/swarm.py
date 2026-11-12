"""Swarm v0.1: deterministic domain prototype; no network calls or LLMs."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import isfinite


def positive_int(value):
    if type(value) is not int or value <= 0:
        raise ValueError('Expected positive integer work units')


@dataclass
class Member:
    owner: str
    provider: str
    team: str
    active: bool = True
    return_after: datetime | None = None


class Room:
    """Single-process trusted core. Authentication belongs in a future server."""
    def __init__(self, contribution=100, cooldown_days=183):
        positive_int(contribution)
        positive_int(cooldown_days)
        self.contribution = contribution
        self.cooldown = timedelta(days=cooldown_days)
        self.members = {}
        self.pool = 0
        self.balances = {'A': 0, 'B': 0, 'referee': 0}
        self.spent = 0
        self.started = False
        self.results = {}
        self.points = {}
        self.notes = []
        # Round lifecycle (board #2). round_id 0 means no round has started yet.
        self.round_id = 0
        self.rounds = {}

    def join(self, owner, provider, team, now):
        if team not in ('A', 'B') or not owner or not provider:
            raise ValueError('Owner, provider and team A/B required')
        if now.tzinfo is None:
            raise ValueError('Timezone-aware clock required')
        old = self.members.get(owner)
        if old and old.active:
            raise ValueError('Owner already active; extra agents do not add membership')
        if old and now < old.return_after:
            raise ValueError('Rejoining cooldown active')
        if self.started:
            raise ValueError('Membership is frozen for the current round')
        self.members[owner] = Member(owner, provider, team)
        self.points.setdefault(owner, 0)
        self.pool += self.contribution

    def start(self):
        """Start round 1. Later rounds use next_round()."""
        if self.round_id:
            raise ValueError('Round already started; use end_round() then next_round()')
        self._begin_round()

    def next_round(self):
        """Start the next round after end_round(); membership may change in between."""
        if self.started:
            raise ValueError('Current round still running; call end_round() first')
        if not self.round_id:
            raise ValueError('No round yet; use start() for round 1')
        self._begin_round()

    def available(self):
        """Committed units not yet spent and not allocated to a running round."""
        return self.pool - self.spent - sum(self.balances.values())

    def _begin_round(self):
        if self.started:
            raise ValueError('Round already started')
        active = sorted(o for o, m in self.members.items() if m.active)
        if {self.members[o].team for o in active} != {'A', 'B'}:
            raise ValueError('Both teams require at least one active owner')
        # Allocate only units that were never spent, so spent units can never
        # become spendable again in a later round.
        budget = self.available()
        # 20% referee/coordination reserve; split remainder equally despite team size.
        referee = budget // 5
        team = (budget - referee) // 2
        self.balances = {'A': team, 'B': team, 'referee': budget - 2 * team}
        self.round_id += 1
        self.rounds[self.round_id] = {
            'members': {o: self.members[o].team for o in active},
            'allocated': dict(self.balances),
            'spent_before': self.spent,
            'ended': False,
        }
        self.started = True

    def end_round(self):
        """Close the running round. Unspent units return to the room's available pool."""
        if not self.started:
            raise ValueError('No running round to end')
        info = self.rounds[self.round_id]
        info['unspent'] = dict(self.balances)
        info['spent'] = self.spent - info['spent_before']
        info['ended'] = True
        self.balances = {'A': 0, 'B': 0, 'referee': 0}
        self.started = False
        return self.round_summary(self.round_id)

    def round_summary(self, round_id):
        if round_id not in self.rounds:
            raise ValueError('Unknown round')
        info = self.rounds[round_id]
        summary = {k: (dict(v) if isinstance(v, dict) else v) for k, v in info.items()}
        summary['round_id'] = round_id
        summary['results'] = sorted(e for e, r in self.results.items() if r['round'] == round_id)
        return summary

    def debit(self, bucket, units):
        positive_int(units)
        if not self.started or bucket not in self.balances:
            raise ValueError('Start round and select a valid budget bucket')
        if units > self.balances[bucket]:
            raise ValueError('Budget exhausted')
        self.balances[bucket] -= units
        self.spent += units

    def leave(self, owner, now):
        member = self._active(owner)
        if now.tzinfo is None:
            raise ValueError('Timezone-aware clock required')
        member.active = False
        member.return_after = now + self.cooldown
        # Committed units stay in the pool; all future access is revoked.

    def _active(self, owner):
        member = self.members.get(owner)
        if member is None or not member.active:
            raise ValueError('Active membership required')
        return member

    def publish_note(self, owner, text, approved_for_sharing):
        self._active(owner)
        if approved_for_sharing is not True or not text.strip():
            raise ValueError('Owner-side sharing approval and nonempty note required')
        self.notes.append({'owner': owner, 'text': text})

    def read_notes(self, owner):
        self._active(owner)
        return [dict(n) for n in self.notes]

    def record_verified_outcome(self, event_id, team, value, credits):
        """Trusted referee input only. Value is a locked-rubric utility in [0,1].

        Caller must verify source evidence outside this prototype. Each owner can
        receive points for discovery, testing or closing through the credits map.
        """
        if not self.started or event_id in self.results or not event_id:
            raise ValueError('Started round and unique outcome ID required')
        if team not in ('A', 'B'):
            raise ValueError('Unknown team')
        if type(value) not in (int, float) or not isfinite(value) or not 0 <= value <= 1:
            raise ValueError('Outcome utility must be finite and between 0 and 1')
        if not credits:
            raise ValueError('Contribution credits required')
        if any(type(w) not in (int, float) or not isfinite(w) or w <= 0 for w in credits.values()):
            raise ValueError('Credit weights must be positive and finite')
        if abs(sum(credits.values()) - 1) > 1e-9:
            raise ValueError('Credit weights must sum to 1')
        if any(o not in self.members or self.members[o].team != team for o in credits):
            raise ValueError('Credit only verified contributors on the producing team')
        self.results[event_id] = {'team': team, 'value': value, 'credits': dict(credits),
                                  'round': self.round_id}
        for owner, weight in credits.items():
            self.points[owner] += 100 * value * weight

    def scoreboard(self, round_id=None):
        """All rounds by default; pass round_id for one round's team totals."""
        if round_id is not None and round_id not in self.rounds:
            raise ValueError('Unknown round')
        totals = {'A': 0.0, 'B': 0.0}
        for result in self.results.values():
            if round_id is None or result['round'] == round_id:
                totals[result['team']] += 100 * result['value']
        winner = None if totals['A'] == totals['B'] else max(totals, key=totals.get)
        individuals = dict(self.points)
        if round_id is not None:
            individuals = {}
            for result in self.results.values():
                if result['round'] == round_id:
                    for owner, weight in result['credits'].items():
                        individuals[owner] = individuals.get(owner, 0) + 100 * result['value'] * weight
        return {'teams': totals, 'individuals': individuals, 'winner': winner,
                'remaining_work_units': dict(self.balances), 'spent_work_units': self.spent,
                'round_id': self.round_id, 'round': round_id}


if __name__ == '__main__':
    from datetime import timezone
    import json
    room = Room()
    now = datetime.now(timezone.utc)
    room.join('agency-alpha', 'provider-one-mock', 'A', now)
    room.join('agency-beta', 'provider-two-mock', 'B', now)
    room.start()
    room.publish_note('agency-alpha', 'Hypothesis: recent public requests may be useful leads.', True)
    room.debit('A', 25)
    room.debit('B', 25)
    room.debit('referee', 10)
    room.record_verified_outcome('mock-result-a', 'A', 0.7, {'agency-alpha': 1.0})
    room.record_verified_outcome('mock-result-b', 'B', 0.6, {'agency-beta': 1.0})
    print(json.dumps({'simulation_only': True, **room.scoreboard()}, indent=2))
