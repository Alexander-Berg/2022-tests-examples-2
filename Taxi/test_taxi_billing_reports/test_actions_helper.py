import pytest

from taxi_billing_reports.actions import helper


@pytest.mark.parametrize(
    'string,pattern,expected',
    [
        ('', '', True),
        ('', '%', True),
        ('', '%%', True),
        ('', '%a', False),
        ('aa', 'aa', True),
        ('aaa', 'aa', False),
        ('aa', '%', True),
        ('aa', 'a%', True),
        ('aab', 'c%a%b', False),
    ],
)
async def test_wildcard_match(string, pattern, expected):
    assert helper.wildcard_match(string, pattern) == expected


@pytest.mark.parametrize(
    'iterables,expected,sort_key,uniq_key',
    [
        (
            [[1, 2, 2, 3], [3, 5, 6], [0, 4, 8]],
            [0, 1, 2, 3, 4, 5, 6, 8],
            lambda x: x,
            lambda x: x,
        ),
        (
            [[3, 2, 2, 1], [6, 5, 3], [8, 4, 0]],
            [8, 6, 5, 4, 3, 2, 1, 0],
            lambda x: -x,
            lambda x: -x,
        ),
    ],
)
async def test_heapq_merge_async(iterables, expected, sort_key, uniq_key):
    async def _make_async_iterable(iterable):
        for item in iterable:
            yield item

    actual = [
        item
        async for item in helper.merge_async(
            *[_make_async_iterable(iterable) for iterable in iterables],
            sort_key=sort_key,
            uniqueness_key=uniq_key,
        )
    ]
    assert actual == expected
