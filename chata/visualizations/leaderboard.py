import matplotlib.pyplot as plt
from dataclasses import dataclass
from bidi.algorithm import get_display
from matplotlib.colors import hsv_to_rgb

from chata.core import PyplotVisualization
from chata.pool import StatPool
from chata.stats import GroupStats, MessagesPerPerson


@dataclass
class Leaderboard(PyplotVisualization):
    messages_per_person: MessagesPerPerson
    group: GroupStats

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(MessagesPerPerson), pool.get(GroupStats))

    def _create_figure(self, max_people=25):
        mpp = [(k, v) for k, v in self.messages_per_person.num_messages_per_person.items() if v > 0]
        max_people = min(max_people, len(mpp))
        labels, sizes = zip(*sorted(mpp, key=lambda t: t[1])[-max_people:])
        labels = [f'{get_display(label)} ({len(labels) - i})' for i, label in enumerate(labels)]
        fig, ax = plt.subplots(figsize=(10, max(len(labels), 5) * 0.4))
        ax.set_title(f'Top {max_people}\n{self.group.title}', pad=40)
        ax.xaxis.tick_top()
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        for i, val in enumerate(sizes):
            ax.text(val + 3, i, str(val))
        best = max(sizes)
        ax.barh(labels, sizes, color=[hsv_to_rgb([(s / best / 3) % 1, 1, 1]) for s in sizes])
        ax.set_ylim(ymin=-0.5, ymax=len(labels) - 0.5)
        plt.tight_layout()
        return fig
