import os
import sys
from dataclasses import dataclass
from bidi.algorithm import get_display

from chata.core import Visualization, NoData
from chata.pool import StatPool
from chata.stats import GroupStats, MessagesPerPerson, PeopleStats


@dataclass
class LeastActive(Visualization):
    group: GroupStats
    messages_per_person: MessagesPerPerson
    people: PeopleStats

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(GroupStats), pool.get(MessagesPerPerson), pool.get(PeopleStats))

    def show(self, last_days=6, threshold=0, io=sys.stdout):
        least_active = []
        for person, join_time in self.people.join_times.items():
            seniority_days = (self.group.last_message_time - join_time).total_seconds() / 60 / 60 / 24
            if seniority_days > last_days and person in self.people.current:
                least_active.append((self.messages_per_person.num_messages_per_person[person],
                                     seniority_days, person))
        least_active = sorted(least_active, key=lambda t: (t[0], -t[1]))
        if not least_active:
            raise NoData()
        print(f'Least active in last {last_days} days:', file=io)
        i = 1
        for amount, seniority_days, person in least_active:
            if amount <= threshold:
                print(f'  {i}. {get_display(person)}: {amount} ({seniority_days:.1f})', file=io)
                i += 1

    def save(self, directory: str):
        with open(os.path.join(directory, f'{type(self).__name__}.txt'), 'w', encoding='utf8') as f:
            self.show(io=f)
