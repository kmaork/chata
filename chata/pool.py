import os
from dataclasses import dataclass, field
from typing import List, Dict, Type, Optional, Iterable

from .events import Event
from .core import EventHandler, Stat, Visualization, NoData


@dataclass
class Visualizations:
    visualizations: list[Visualization]

    def show(self):
        types = set(map(type, self.visualizations))
        for vis_type in types:
            vis_type.pre_show()
        for vis in self.visualizations:
            try:
                vis.show()
            except NoData:
                pass
        for vis_type in types:
            vis_type.post_show()

    def save(self, directory: str):
        os.makedirs(directory, exist_ok=True)
        for vis in self.visualizations:
            try:
                vis.save(directory)
            except NoData:
                pass


@dataclass
class StatPool:
    event_handlers: List[EventHandler] = field(default_factory=list)
    map: Dict[Type[Stat], Stat] = field(default_factory=dict)

    def _add(self, stat_type: Type[Stat], args, key):
        stat = stat_type.from_pool(self, *args)
        if isinstance(stat, EventHandler):
            self.event_handlers.append(stat)
        self.map[key] = stat
        return stat

    def get(self, stat_type: Type[Stat], *args):
        key = stat_type, args
        if key in self.map:
            return self.map[key]
        return self._add(stat_type, args, key)

    def _handle(self, event: Event):
        for handler in self.event_handlers:
            handler.handle(event)

    def yield_lines(self, messages_file: str, max_lines: Optional[int]):
        with open(messages_file, 'r', encoding='utf8') as f:
            for i, line in enumerate(f):
                # Random characters for handling RTL that whatsapp puts in the exported file
                yield line.rstrip('\n')
                if max_lines is not None and i >= max_lines:
                    break

    def devour(self, messages_file: str, max_lines: Optional[int] = None):
        for event in Event.yield_events(self.yield_lines(messages_file, max_lines)):
            self._handle(event)


def visualize(messages_file: str, visualization_types: Iterable[Type[Visualization]] = None):
    if visualization_types is None:
        import chata.visualizations
        visualization_types = [getattr(chata.visualizations, a) for a in chata.visualizations.__all__]
    pool = StatPool()
    visualizations = [visualization_type.from_pool(pool) for visualization_type in visualization_types]
    pool.devour(messages_file)
    return Visualizations(visualizations)
