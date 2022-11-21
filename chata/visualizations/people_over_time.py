import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dataclasses import dataclass

from chata.core import PyplotVisualization
from chata.pool import StatPool
from chata.stats import GroupStats, PeopleStats, EventOverTime, AddsOverTime, LeftOverTime
from chata.events import Removed, Joined


@dataclass
class PeopleOverTime(PyplotVisualization):
    group: GroupStats
    people: PeopleStats
    kicks_over_time: EventOverTime
    joined_over_time: EventOverTime
    adds_over_time: AddsOverTime
    left_over_time: LeftOverTime

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(GroupStats), pool.get(PeopleStats), pool.get(EventOverTime, Removed),
                   pool.get(EventOverTime, Joined), pool.get(AddsOverTime), pool.get(LeftOverTime))

    def add_start_and_end(self, times, amounts):
        return ([self.group.first_message_time, *times, self.group.last_message_time],
                [0, *amounts, amounts[-1]])

    def _create_figure(self):
        fig, ax = plt.subplots()
        ax.set_title(f'People over time\n{self.group.title}')
        ax.set_xlabel('Time')
        ax.set_ylabel('Amount')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.plot(*zip(*self.people.total_over_time))
        ax.plot(*self.add_start_and_end(*self.joined_over_time.get_sorted()))
        ax.plot(*self.add_start_and_end(*self.left_over_time.get_sorted()))
        ax.plot(*zip(*self.people.amount_over_time))
        ax.plot(*self.add_start_and_end(*self.kicks_over_time.get_sorted()))
        ax.plot(*self.add_start_and_end(*self.adds_over_time.get_sorted()))
        ax.legend(['Total people', 'Total joined', 'Total left', 'Current people', 'Total removed', 'Total added'],
                  loc='upper left')
        ax.set_ylim(ymin=0)
        return fig
