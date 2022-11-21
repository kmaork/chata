from __future__ import annotations

import os
from abc import abstractmethod, ABCMeta
from typing import Dict, Callable, Type, TYPE_CHECKING, Any

import matplotlib
from matplotlib import pyplot as plt

from .events import Event

if TYPE_CHECKING:
    from .pool import StatPool


class NoData(Exception):
    pass


class Stat(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_pool(cls, pool: StatPool, *args):
        raise NotImplementedError()


class Visualization(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_pool(cls, pool: StatPool):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def save(self, directory: str):
        pass

    @classmethod
    def pre_show(cls):
        pass

    @classmethod
    def post_show(cls):
        pass


class PyplotVisualization(Visualization):
    @abstractmethod
    def _create_figure(self):
        pass

    def show(self):
        self._create_figure().show()

    def save(self, directory: str = '.'):
        self._create_figure().savefig(f'{os.path.join(directory, type(self).__name__)}.png')

    @classmethod
    def pre_show(cls):
        # TODO
        # matplotlib.rcParams['font.family'] = "Some native font with better glyph coverage?"
        pass

    @classmethod
    def post_show(cls):
        plt.show()


class EventHandler(Stat, metaclass=ABCMeta):
    __handlers: Dict[Type[Event], Callable[[EventHandler, Event], Any]] = {}

    def set_instance_handlers(self, handlers):
        self.__handlers = {**self.__handlers, **handlers}

    @classmethod
    def __init_subclass__(cls, **kwargs):
        this_handlers = {handler.event_type: handler.func
                         for handler in vars(cls).values()
                         if isinstance(handler, Handler)}
        cls.__handlers = {**super(cls, cls).__handlers, **this_handlers}

    def handle(self, event: Event):
        handler = self.__handlers.get(type(event))
        if handler is not None:
            handler(self, event)


class Handler:
    def __init__(self, event_type: Type[Event]):
        self.event_type = event_type

    def __call__(self, func: Callable[[EventHandler, Event], Any]):
        self.func = func
        return self
