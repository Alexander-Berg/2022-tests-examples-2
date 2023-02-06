# pylint: disable=protected-access

import pytest

from mia.crontasks.formatter import formatter


@pytest.mark.parametrize(
    'key_path, default_value, expected',
    [
        ('a', None, None),
        ('a', 'default', None),
        ('b', None, '1'),
        ('b', 'default', '1'),
        ('c', None, {'d': None, 'e': '2'}),
        ('c', 'default', {'d': None, 'e': '2'}),
        ('e', None, None),
        ('e', 'default', 'default'),
        ('c.d', None, None),
        ('c.d', 'default', None),
        ('c.e', None, '2'),
        ('c.e', 'default', '2'),
        ('c.a', None, None),
        ('c.a', 'default', 'default'),
    ],
)
async def test_get_value(key_path, default_value, expected):
    doc = {'a': None, 'b': '1', 'c': {'d': None, 'e': '2'}}

    value = formatter.Formatter._get_value(doc, key_path, default_value)
    assert value == expected


@pytest.mark.parametrize(
    'timestamp, timezone, expected',
    [
        (None, None, None),
        (1551732995.45, 'Europe/Moscow', '04.03.2019 23:56:35+0300'),
        (1551732995.45, 'Europe/Rome', '04.03.2019 21:56:35+0100'),
    ],
)
async def test_format_time(timestamp, timezone, expected):
    formatted_time = formatter.Formatter._format_time(timestamp, timezone)
    assert formatted_time == expected
