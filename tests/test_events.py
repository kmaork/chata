from chata.events import Message
import datetime as dt

def test_parsing_multiline_message():
    message = Message._parse('1/2/03, 04:05 - lol: a\nb\nc')
    assert message.time == dt.datetime(2003, 1, 2, 4, 5)
    assert message.who == 'lol'
    assert message.message == 'a\nb\nc'
