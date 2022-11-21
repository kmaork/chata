import matplotlib.pyplot as plt
from dataclasses import dataclass
import matplotlib.dates as mdates

from chata.core import PyplotVisualization
from chata.pool import StatPool
from chata.stats import GroupStats, MessagesPerDay as MessagesPerDayStat


@dataclass
class MessagesPerDay(PyplotVisualization):
    group: GroupStats
    messages_per_day: MessagesPerDayStat

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(GroupStats), pool.get(MessagesPerDayStat))

    def _create_figure(self):
        fig, ax = plt.subplots()
        ax.set_title(f'Messages per day\n{self.group.title}')
        mpd = dict(self.messages_per_day.buckets)
        # Last day ain't over yet
        mpd.pop(max(mpd))
        dates, nums = zip(*mpd.items())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        ax.plot(dates, nums)
        ax.set_ylim(ymin=0, ymax=max(nums) + 100)
        ax.set_ylabel('Amount')
        ax.set_xlabel('Date')
        return fig
