import re
from dataclasses import dataclass
import datetime as dt
from functools import cached_property

BASE = '^(?P<_time>.+?) - '
WHO = '(?P<who>.+?)'

def all_subclasses(cls):
    return [cls, *(c for sc in map(all_subclasses, cls.__subclasses__()) for c in sc)]


def split_word_list(word_list):
    '''
    assert split_word_list('a') == ['a']
    assert split_word_list('a and b') == ['a', 'b']
    assert split_word_list('a, b, and c') == ['a', 'b', 'c']
    assert split_word_list('a, b, c, and d') == ['a', 'b', 'c', 'd']
    '''
    *firsts, lasts = word_list.split(', ')
    if firsts:
        return [*firsts, lasts[len('and '):]]
    return [*firsts, *lasts.split(' and ')]


@dataclass
class NotMatchedException(Exception):
    regex: re.Pattern
    line: str


@dataclass
class NoMatchException(Exception):
    string: str


class WordSetConverter:
    def __set_name__(self, owner, name):
        self.attr = f'_{name}'

    def __get__(self, instance, owner=None):
        return set(split_word_list(getattr(instance, self.attr)))


@dataclass
class Event:
    REGEX = None
    LIKELIHOOD = 1

    def __init_subclass__(cls, regex=None, flags=0):
        cls.REGEX = None if regex is None else re.compile(regex, flags=flags)

    _time: str

    @classmethod
    def from_string(cls, line):
        match = cls.REGEX.match(line)
        if match is None:
            raise NotMatchedException(cls.REGEX, line)
        return cls(**match.groupdict())

    @classmethod
    def _parse(cls, string: str):
        for i, event_type in enumerate(ALL_EVENT_TYPES):
            try:
                return event_type.from_string(string)
            except NotMatchedException:
                pass
        raise NoMatchException(string)

    @classmethod
    def yield_events(cls, line_generator):
        last_event = None
        last_str = None
        for line in line_generator:
            line = line.replace('\u200e', '').replace('\u202b', '').replace('\u202c', '')
            if last_event is None:
                last_str = line
                last_event = cls._parse(last_str)
            else:
                try:
                    current_event = cls._parse(line)
                except NoMatchException:
                    last_str = f'{last_str}\n{line}'
                    last_event = cls._parse(last_str)
                else:
                    yield last_event
                    last_str = line
                    last_event = current_event
        yield current_event

    @cached_property
    def time(self):
        """ 6x faster than strptime """
        t = self._time
        i = t.find('/')
        month = int(t[:i])
        i2 = t.find('/', i + 1)
        day = int(t[i + 1:i2])
        year = int(t[i2 + 1:i2 + 3]) + 2000
        hour = int(t[i2 + 5:i2 + 7])
        minute = int(t[i2 + 8:i2 + 10])
        return dt.datetime(year, month, day, hour, minute)
        # return dt.datetime.strptime(self._time, '%m/%d/%y, %H:%M')


@dataclass
class Encrypted(Event, regex=f'{BASE}Messages and calls are end-to-end encrypted. ' \
                             'No one outside of this chat, not even WhatsApp, ' \
                             'can read or listen to them. Tap to learn more.$'):
    pass


@dataclass
class Left(Event, regex=f'{BASE}(?P<_left>.+?) left$'):
    _left: str
    left = WordSetConverter()


@dataclass
class Admin(Event, regex=f'{BASE}You\'re now an admin$'):
    pass


@dataclass
class AnonymousAdd(Event, regex=f'{BASE}(?P<_added>.+?) was added$'):
    _added: str
    added = WordSetConverter()


@dataclass
class Action(Event):
    who: str


@dataclass
class Created(Action, regex=f'{BASE}{WHO} created group "(?P<name>.+?)"$'):
    name: str


@dataclass
class YouChangedGroupDescription(Action, regex=f'{BASE}{WHO} changed the group description'):
    pass


@dataclass
class SubjectChanged(Action, regex=f'{BASE}{WHO} changed the subject from "(?P<old_name>.+?)" ' \
                                   'to "(?P<new_name>.+?)"$'):
    old_name: str
    new_name: str


@dataclass
class IconChanged(Action, regex=f'{BASE}{WHO} changed this group\'s icon$'):
    pass


@dataclass
class IconDeleted(Action, regex=f'{BASE}{WHO} deleted this group\'s icon$'):
    pass


@dataclass
class SettingsChanged(Action, regex=f'{BASE}{WHO} changed this group\'s settings to ' \
                                    'allow only admins to edit this group\'s info$'):
    pass


@dataclass
class Message(Action, regex=f'{BASE}{WHO}: (?P<message>.+?)$', flags=re.DOTALL):
    LIKELIHOOD = 0

    message: str


@dataclass
class SecurityCodeChanged(Action, regex=f'{BASE}{WHO}\'s security code changed. Tap for more info.$'):
    pass


@dataclass
class SecurityCodeChangedWith(Action, regex=f'{BASE}Your security code with {WHO} changed. Tap to learn more.$'):
    pass


@dataclass
class Added(Action, regex=f'{BASE}{WHO} added (?P<_added>.+?)$'):
    _added: str
    added = WordSetConverter()


@dataclass
class Removed(Action, regex=f'{BASE}{WHO} removed (?P<removed>.+?)$'):
    removed: str


@dataclass
class Joined(Action, regex=f'{BASE}{WHO} joined using this group\'s invite link$'):
    pass


@dataclass
class TurnedOnDisappearing(Action, regex=f'{BASE}{WHO} turned on disappearing messages. New messages will disappear '
                                         f'from this chat after 7 days. Tap to change.'):
    pass


@dataclass
class TurnedOffDisappearing(Action, regex=f'{BASE}{WHO} turned off disappearing messages. Tap to change.'):
    pass


ALL_EVENT_TYPES = sorted(filter(lambda sc: sc.REGEX is not None, all_subclasses(Event)), key=lambda sc: sc.LIKELIHOOD)
