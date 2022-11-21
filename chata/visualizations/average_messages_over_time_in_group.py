import matplotlib.pyplot as plt
from collections import defaultdict
from dataclasses import dataclass

from chata.core import PyplotVisualization, NoData
from chata.pool import StatPool
from chata.stats import GroupStats, MessagesPerSeniority


def divide(values_map, amount):
    groups = []
    sort = sorted(values_map, key=lambda key: values_map[key])
    amount_in_group = len(values_map) / amount
    last = 0
    for i in range(1, amount + 1):
        current = int(round(i * amount_in_group))
        groups.append(sort[last:current])
        last = current
    return groups


@dataclass
class Average:
    sum: float = 0.
    num: int = 0

    def __iadd__(self, other):
        self.sum += other
        self.num += 1
        return self

    @property
    def value(self):
        return self.sum / self.num


@dataclass
class AverageMessagesOverTimeInGroup(PyplotVisualization):
    group: GroupStats
    messages_per_seniority: MessagesPerSeniority

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls(pool.get(GroupStats), pool.get(MessagesPerSeniority))

    def get_averages_per_seniority(self, num_groups):
        mpsbp = {k: dict(v) for k, v in self.messages_per_seniority.messages_by_seniority_by_person.items()
                 if len(v) > 1}  # we're ignoring the last day
        if len(mpsbp) <= 2:
            raise NoData()
        for person, mps in mpsbp.items():
            # ignoring last day because it is incomplete
            mps.pop(max(mps))
        groups = divide({person: sum(mps.values()) / (max(mps) + 1)
                         for person, mps in mpsbp.items()}, num_groups)
        averages_per_seniority = []
        for group in groups:
            average_per_seniority = defaultdict(Average)
            for person in group:
                mps = mpsbp[person]
                for seniority, messages in mps.items():
                    average_per_seniority[seniority] += messages
            if average_per_seniority:
                averages_per_seniority.append({seniority: average.value
                                               for seniority, average in average_per_seniority.items()})
        return averages_per_seniority

    def _create_figure(self):
        percentages = 5
        averages_per_seniority = self.get_averages_per_seniority(percentages)
        fig, ax = plt.subplots()
        ax.set_title(f'Average messages per day over seniority in group\n{self.group.title}')
        for average_percents_per_seniority in averages_per_seniority:
            for seniority in range(max(average_percents_per_seniority)):
                average_percents_per_seniority.setdefault(seniority, 0)
            xs, ys = zip(*sorted(average_percents_per_seniority.items()))
            ax.plot(xs, ys)
        ax.set_xlabel('Days in group')
        ax.set_ylabel('Average messages')
        ax.legend([f'{n * 100 // percentages}% - {(n + 1) * 100 // percentages}%' for n in range(percentages)])
        return fig
