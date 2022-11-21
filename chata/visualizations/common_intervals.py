import matplotlib.pyplot as plt
from dataclasses import dataclass

from chata.core import PyplotVisualization
from chata.pool import StatPool
from chata.stats import GroupStats, MessagesPerTimeDelta


@dataclass
class CommonIntervals(PyplotVisualization):
    messages_per_dt: MessagesPerTimeDelta
    group: GroupStats

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(MessagesPerTimeDelta), pool.get(GroupStats))

    def _create_figure(self):
        fig, ax = plt.subplots()
        ax.set_title(f'Intervals between messages\n{self.group.title}')
        tds, sizes = zip(*sorted(self.messages_per_dt.buckets.items(), key=lambda t: -t[1]))
        td_str = lambda td: f'{int(td.total_seconds() / 60)}min'
        labels = [f'>= {td_str(MessagesPerTimeDelta.TDS[-1])}' if td is None else f'< {td_str(td)}' for td in tds]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', pctdistance=0.85, startangle=180, labeldistance=1.05)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        return fig
