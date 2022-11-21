import os
import sys
from dataclasses import dataclass

from chata.core import Visualization
from chata.pool import StatPool
from chata.stats import GroupStats


@dataclass
class GroupNames(Visualization):
    group: GroupStats

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(GroupStats))

    def show(self, io=sys.stdout):
        print('Names the group had:', file=io)
        for name in self.group.names:
            print(f'  {name}', file=io)

    def save(self, directory: str):
        with open(os.path.join(directory, f'{type(self).__name__}.txt'), 'w', encoding='utf8') as f:
            self.show(io=f)
