import datetime as dt
from dataclasses import dataclass, field
from typing import Optional

from bidi.algorithm import get_display

from chata.events import Message, Created, SubjectChanged, Encrypted
from chata.core import EventHandler, Handler
from chata.pool import StatPool


@dataclass
class GroupStats(EventHandler):
    num_messages: int = 0
    names: list[str] = field(default_factory=list)
    first_message_time: Optional[dt.datetime] = None
    last_message_time: Optional[dt.datetime] = None
    create_time: Optional[dt.datetime] = None
    is_first_msg: bool = True
    default_name: str = 'Whatsapp Conversation'

    @property
    def name(self) -> str:
        return self.names[-1] if self.names else self.default_name

    @classmethod
    def from_pool(cls, pool: StatPool):
        return cls()

    @staticmethod
    def _format_dt(time: dt.datetime):
        return time.date().strftime('%b %d, %y')

    @property
    def time_range(self) -> str:
        return f'{self._format_dt(self.first_message_time)} - {self._format_dt(self.last_message_time)}'

    @property
    def title(self) -> str:
        return f'{get_display(self.name)} ({self.time_range})'

    @Handler(Message)
    def handle_message(self, message):
        if self.is_first_msg:
            self.first_message_time = message.time
            self.is_first_msg = False
        self.num_messages += 1
        self.last_message_time = message.time

    @Handler(Created)
    def handle_created(self, created):
        if created.name is not None:
            self.names.append(created.name)
        self.create_time = created.time

    @Handler(SubjectChanged)
    def handle_subject_changed(self, change):
        self.names.append(change.new_name)

    @Handler(Encrypted)
    def handle_encrypted(self, encrypted: Encrypted):
        if encrypted.group_name is not None:
            self.default_name = encrypted.group_name
