import datetime as dt
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional

from chata.core import EventHandler, Handler
from chata.pool import StatPool
from chata.events import Message

from .people import PeopleStats


class MessagesPer(EventHandler, metaclass=ABCMeta):
    IGNORE = object()

    def __init__(self):
        self.buckets = defaultdict(int)

    @abstractmethod
    def _get_bucket(self, message: Message):
        pass

    @Handler(Message)
    def handle_message(self, message: Message):
        bucket = self._get_bucket(message)
        if bucket is not self.IGNORE:
            self.buckets[bucket] += 1


class MessagesPerPerson(MessagesPer):
    def __init__(self, people: PeopleStats):
        super().__init__()
        self.people = people

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(PeopleStats))

    def _get_bucket(self, message: Message):
        return message.who

    @property
    def num_messages_per_person(self):
        mpp = dict(self.buckets)
        for person in self.people.all_time:
            mpp.setdefault(person, 0)
        return mpp


class MessagesPerDay(MessagesPer):
    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls()

    def _get_bucket(self, message: Message):
        return message.time.date()


class MessagesPerHour(MessagesPer):
    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls()

    def _get_bucket(self, message: Message):
        return message.time.hour


class MessagesPerWeekDay(MessagesPer):
    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls()

    def _get_bucket(self, message: Message):
        return message.time.weekday()


class MessagesPerTimeDelta(MessagesPer):
    TDS = sorted([dt.timedelta(minutes=1),
                  dt.timedelta(minutes=2),
                  dt.timedelta(minutes=4),
                  dt.timedelta(minutes=8)])
    last_time: Optional[int] = None

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls()

    def _find_delta(self, delta: dt.timedelta):
        for td in self.TDS:
            if td > delta:
                return td
        return None

    def _get_bucket(self, message: Message):
        last_time = self.last_time
        self.last_time = message.time
        if last_time is None:
            return self.IGNORE
        return self._find_delta(message.time - last_time)


@dataclass
class MessagesPerSeniority(EventHandler):
    people_stats: PeopleStats
    messages_by_seniority_by_person: Dict[str, Dict[int, int]] = \
        field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(PeopleStats))

    @Handler(Message)
    def handle_message(self, message: Message):
        join_time = self.people_stats.join_times[message.who]
        seniority_days = int((message.time - join_time).total_seconds() / 60 / 60 / 24)
        self.messages_by_seniority_by_person[message.who][seniority_days] += 1
