import os
import sys
from dataclasses import dataclass

from chata.core import Visualization
from chata.pool import StatPool
from chata.stats import PeopleStats


@dataclass
class TotalPeople(Visualization):
    people: PeopleStats

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(PeopleStats))

    def show(self, io=sys.stdout):
        print(f'Total people that have been in the group: {len(self.people.all_time)}', file=io)

    def save(self, directory: str):
        with open(os.path.join(directory, f'{type(self).__name__}.txt'), 'w', encoding='utf8') as f:
            self.show(io=f)
