import matplotlib.pyplot as plt
from dataclasses import dataclass

from chata.core import PyplotVisualization
from chata.pool import StatPool
from chata.stats import GroupStats, MessagesPerWeekDay


@dataclass
class FrequentDays(PyplotVisualization):
    group: GroupStats
    messages_per_day: MessagesPerWeekDay

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(GroupStats), pool.get(MessagesPerWeekDay))

    def _create_figure(self):
        fig, ax = plt.subplots()
        ax.set_title(f'Activity by weekday\n{self.group.title}')
        ax.yaxis.set_major_formatter('{x:.0f}%')
        days, sizes = zip(*sorted(self.messages_per_day.buckets.items()))
        total = sum(sizes)
        percs = [size / total * 100 for size in sizes]
        labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        # Stack it in four groups, 2-8, 8-14, 14-20, 20-2
        ax.bar(labels, percs, 0.35)
        return fig
