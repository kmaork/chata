from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any

from chata.events import Event, Action, Joined, Left, AnonymousAdd, Removed, Added, Created
from chata.core import EventHandler, Handler
from chata.pool import StatPool

Person = str


@dataclass
class PeopleTracker(EventHandler):
    aliases: Dict[Person, Person] = field(default_factory=dict)
    add_callbacks: List[Callable[[Person, Event], Any]] = field(default_factory=list)
    remove_callbacks: List[Callable[[Person, Event], Any]] = field(default_factory=list)

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls()

    def _get_original(self, person):
        return self.aliases.get(person, person)

    def add_add_callback(self, callback: Callable[[Person, Event], Any]):
        self.add_callbacks.append(callback)

    def add_remove_callback(self, callback: Callable[[Person, Event], Any]):
        self.remove_callbacks.append(callback)

    def _add(self, person: Person, event: Event):
        original = self._get_original(person)
        for callback in self.add_callbacks:
            callback(original, event)

    def _remove(self, person: Person, event: Event):
        original = self._get_original(person)
        for callback in self.remove_callbacks:
            callback(original, event)

    def handle(self, event: Event):
        super().handle(event)
        if isinstance(event, Action):
            self._add(event.who, event)  # Until can handle edge cases

    @Handler(Joined)
    def _handle_joined(self, joined: Joined):
        self._add(joined.who, joined)

    @Handler(Left)
    def _handle_left(self, left: Left):
        for person in left.left:
            self._remove(person, left)

    @Handler(AnonymousAdd)
    def _handle_anon_add(self, add: AnonymousAdd):
        for person in add.added:
            self._add(person, add)

    @Handler(Removed)
    def _handle_removed(self, removed: Removed):
        self._remove(removed.removed, removed)

    @Handler(Added)
    def _handle_added(self, added: Added):
        for person in added.added:
            self._add(person, added)

    @Handler(Created)
    def _handle_created(self, created):
        self._add(created.who, created)
