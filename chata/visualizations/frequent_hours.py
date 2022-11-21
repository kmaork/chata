from math import pi

import matplotlib.pyplot as plt
from dataclasses import dataclass

from chata.core import PyplotVisualization
from chata.pool import StatPool
from chata.stats import GroupStats, MessagesPerHour


@dataclass
class FrequentHours(PyplotVisualization):
    group: GroupStats
    messages_per_hour: MessagesPerHour

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(GroupStats), pool.get(MessagesPerHour))

    def _create_figure(self):
        fig, ax = plt.subplots(subplot_kw=dict(polar=True))
        ax.set_title(f'Active hours\n{self.group.title}')
        hours = sorted(self.messages_per_hour.buckets)
        categories = [f'{h:02}:00' for h in hours]
        n = len(categories)
        values = [self.messages_per_hour.buckets[hour] for hour in hours]
        circle = 2 * pi
        angles = [((-a / n + 0.25) * circle) % circle for a in range(n)]
        plt.xticks(angles, categories, color='grey', size=8)
        ax.yaxis.set_ticklabels([])
        ax.plot([*angles, angles[0]], [*values, values[0]], linewidth=1, linestyle='solid')
        ax.fill([*angles, angles[0]], [*values, values[0]], 'b', alpha=0.1)
        plt.subplots_adjust(top=0.85)
        return fig
