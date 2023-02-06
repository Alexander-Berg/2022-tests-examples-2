# pylint: disable=protected-access

import pytest

from mia.crontasks.extra_fetcher import extra_fetcher


class _TestCase:
    def __init__(self, request=None, expected=None):
        self.request = request
        self.expected = expected


@pytest.mark.parametrize(
    'test',
    [
        _TestCase(request={'timestamp': 1591927312}, expected='2020-06'),
        _TestCase(request={'timestamp': 1546563961}, expected='2019-01'),
        _TestCase(request={'timestamp': 1607742000}, expected='2020-12'),
        _TestCase(request={'timestamp': 1585701000}, expected='2020-04'),
        _TestCase(request={'timestamp': 1588289400}, expected='2020-04'),
    ],
)
async def test_timestamp_to_year_month(test):
    request = test.request
    expected = test.expected

    timestamp = request['timestamp']
    result = extra_fetcher.ExtraFetcher._timestamp_to_month(timestamp)

    assert result == expected
