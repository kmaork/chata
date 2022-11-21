from chata.visualizations.average_messages_over_time_in_group import divide


def test_divide():
    assert divide({'a': 2, 'b': -1, 'c': 1}, 3) == [['b'], ['c'], ['a']]
    assert divide({'a': 2, 'b': -1, 'c': 1, 'd': -40, 'e': 0, 'f': 2}, 3) == \
           [['d', 'b'], ['e', 'c'], ['a', 'f']]
    assert divide({'a': 1, 'b': 2}, 1) == [['a', 'b']]
