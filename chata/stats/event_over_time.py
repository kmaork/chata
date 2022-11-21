import datetime as dt
from dataclasses import dataclass, field
from typing import List, Type, Tuple

from chata.core import EventHandler, Handler
from chata.events import Event, Added, AnonymousAdd, Left
from chata.pool import StatPool


def gen_cumsum(it):
    sum = 0
    for i in it:
        sum += i
        yield sum


def cumsum(it):
    return list(gen_cumsum(it))


@dataclass
class EventOverTime(EventHandler):
    event_type: Type[Event]
    times: List[dt.datetime] = field(default_factory=list)

    @classmethod
    def from_pool(cls, pool: StatPool, event_type):
        return cls(event_type)

    def __post_init__(self):
        self.set_instance_handlers({self.event_type: self.handle_event.__func__})

    def handle_event(self, event):
        self.times.append(event.time)

    def get_sorted(self):
        return sorted(self.times), range(1, len(self.times) + 1)


@dataclass
class AddsOverTime(EventHandler):
    pairs: List[Tuple[dt.datetime, int]] = field(default_factory=list)

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls()

    def _add(self, time, amount):
        self.pairs.append((time, amount))

    @Handler(Added)
    def handle_added(self, added: Added):
        self._add(added.time, len(added.added))

    @Handler(AnonymousAdd)
    def handle_added(self, anon_add: AnonymousAdd):
        self._add(anon_add.time, len(anon_add.added))

    def get_sorted(self):
        times, amounts = zip(*sorted(self.pairs))
        return times, cumsum(amounts)


@dataclass
class LeftOverTime(EventHandler):
    pairs: List[Tuple[dt.datetime, int]] = field(default_factory=list)

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls()

    @Handler(Left)
    def handle_left(self, left: Left):
        self.pairs.append((left.time, len(left.left)))

    def get_sorted(self):
        times, amounts = zip(*sorted(self.pairs))
        return times, cumsum(amounts)
