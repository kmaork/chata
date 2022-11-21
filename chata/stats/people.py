import datetime as dt
from dataclasses import dataclass, field
from typing import Set, Dict, List, Tuple

from chata.core import Stat
from chata.pool import StatPool
from chata.events import Event

from .people_tracker import PeopleTracker, Person


@dataclass
class PeopleStats(Stat):
    current: Set[Person] = field(default_factory=set)
    all_time: Set[Person] = field(default_factory=set)
    join_times: Dict[Person, dt.datetime] = field(default_factory=dict)
    _current_over_time: List[Tuple[dt.datetime, int]] = field(default_factory=list)
    _total_over_time: List[Tuple[dt.datetime, int]] = field(default_factory=list)

    @classmethod
    def from_pool(cls, pool: StatPool):
        self = cls()
        tracker = pool.get(PeopleTracker)
        tracker.add_add_callback(self.add)
        tracker.add_remove_callback(self.remove)
        return self

    def add(self, person: Person, event: Event):
        self.current.add(person)
        self.all_time.add(person)
        self.join_times.setdefault(person, event.time)
        self._current_over_time.append((event.time, len(self.current)))
        self._total_over_time.append((event.time, len(self.all_time)))

    def remove(self, person: Person, event: Event):
        try:
            self.current.remove(person)
        except KeyError:
            # Not strict until we can handle edge cases
            pass
        self._current_over_time.append((event.time, len(self.current)))

    @property
    def amount_over_time(self):
        return sorted(self._current_over_time)

    @property
    def total_over_time(self):
        return sorted(self._total_over_time)
