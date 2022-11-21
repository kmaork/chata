import matplotlib.pyplot as plt
from dataclasses import dataclass
from bidi.algorithm import get_display

from chata.core import PyplotVisualization
from chata.pool import StatPool
from chata.stats import GroupStats, MessagesPerPerson


@dataclass
class MostActive(PyplotVisualization):
    messages_per_person: MessagesPerPerson
    group: GroupStats

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(MessagesPerPerson), pool.get(GroupStats))

    def _create_figure(self, max_people=9):
        fig, ax = plt.subplots()
        ax.set_title(f'Messages per person\n{self.group.title}')
        labels, sizes = zip(*sorted(self.messages_per_person.num_messages_per_person.items(), key=lambda t: -t[1]))
        labels = list(map(get_display, labels))[:max_people]
        others = sum(sizes[max_people:])
        extra_data = [others] if others else []
        extra_labels = ['Others'] if others else []
        sizes = sizes[:max_people]
        # https://matplotlib.org/3.3.3/gallery/pie_and_polar_charts/pie_and_donut_labels.html
        ax.pie([*extra_data, *sizes], labels=[*extra_labels, *labels], autopct='%1.1f%%',
               pctdistance=0.85, startangle=210, labeldistance=1.05)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        return fig
