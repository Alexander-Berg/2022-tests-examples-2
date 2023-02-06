from typing import List

import pytest

import intervals.intervals as ints


@pytest.mark.parametrize(
    'interval, value, expected',
    [
        (ints.closed(1, 3), 1, True),
        (ints.closed(1, 3), 2, True),
        (ints.closed(1, 3), 3, True),
        (ints.closed(1, 3), 0, False),
        (ints.closed(1, 3), 5, False),
        (ints.closed_open(1, 3), 1, True),
        (ints.closed_open(1, 3), 2, True),
        (ints.closed_open(1, 3), 3, False),
        (ints.closed_open(1, 3), 0, False),
        (ints.closed_open(1, 3), 5, False),
        (ints.singleton(1), 0, False),
        (ints.singleton(1), 1, True),
        (ints.singleton(1), 2, False),
        (ints.at_least(5), 6, True),
        (ints.at_least(5), 4, False),
        (ints.at_least(5), 5, True),
        (ints.unbounded(), 0, True),
    ],
)
@pytest.mark.nofilldb()
def test_contains(interval: ints.Interval[int], value: int, expected: bool):
    assert expected == (value in interval)


@pytest.mark.parametrize(
    'interval, expected',
    [
        (ints.closed(1, 3), False),
        (ints.closed(1, 1), False),
        (ints.closed_open(1, 1), True),
        (ints.closed_open(1, 2), False),
        (ints.singleton(1), False),
        (ints.at_least(4), False),
        (ints.unbounded(), False),
    ],
)
@pytest.mark.nofilldb()
def test_is_empty(interval: ints.Interval[int], expected: bool):
    assert expected == interval.is_empty()


@pytest.mark.parametrize(
    'int1, int2, expected',
    [
        (ints.closed(1, 3), ints.closed(3, 4), True),
        (ints.closed(1, 3), ints.closed(4, 4), False),
        (ints.closed(3, 4), ints.closed(2, 3), True),
        (ints.closed(3, 4), ints.closed(1, 2), False),
        (ints.closed_open(1, 3), ints.closed(3, 4), True),
        (ints.closed_open(1, 3), ints.closed(4, 4), False),
        (ints.closed(3, 4), ints.closed_open(2, 3), True),
        (ints.closed(3, 4), ints.closed_open(1, 2), False),
        (ints.closed(3, 5), ints.singleton(4), True),
        (ints.closed_open(3, 5), ints.singleton(5), True),
        (ints.closed_open(3, 5), ints.at_least(5), True),
        (ints.closed_open(3, 5), ints.at_least(6), False),
        (ints.at_least(1), ints.closed(3, 5), True),
        (ints.unbounded(), ints.singleton(3), True),
    ],
)
@pytest.mark.nofilldb()
def test_is_connected(int1, int2: ints.Interval[int], expected: bool):
    assert expected == int1.is_connected(int2)


@pytest.mark.parametrize(
    'int1, int2, expected',
    [
        (ints.singleton(1), ints.singleton(1), ints.singleton(1)),
        (ints.closed(1, 3), ints.closed(2, 4), ints.closed(2, 3)),
        (ints.closed(2, 3), ints.closed(1, 2), ints.singleton(2)),
        (ints.closed_open(1, 3), ints.closed(3, 4), ints.closed_open(3, 3)),
        (
            ints.closed_open(1, 5),
            ints.closed_open(3, 4),
            ints.closed_open(3, 4),
        ),
        (
            ints.closed_open(1, 5),
            ints.closed_open(3, 6),
            ints.closed_open(3, 5),
        ),
        (ints.closed(1, 5), ints.closed(2, 4), ints.closed(2, 4)),
        (ints.closed(2, 4), ints.closed(0, 5), ints.closed(2, 4)),
        (ints.closed(2, 4), ints.at_least(0), ints.closed(2, 4)),
        (ints.closed(2, 4), ints.at_least(3), ints.closed(3, 4)),
        (ints.unbounded(), ints.at_least(3), ints.at_least(3)),
    ],
)
@pytest.mark.nofilldb()
def test_intersection(int1, int2, expected: ints.Interval[int]):
    assert expected == int1.intersection(int2)


@pytest.mark.parametrize(
    'int1, int2, expected',
    [
        (ints.closed(1, 5), ints.closed(1, 5), True),
        (ints.singleton(1), ints.singleton(1), True),
        (ints.closed(1, 3), ints.closed(3, 4), True),
        (ints.closed(1, 3), ints.closed(4, 4), False),
        (ints.closed(3, 4), ints.closed(2, 3), True),
        (ints.closed(3, 4), ints.closed(1, 2), False),
        (ints.closed_open(1, 3), ints.closed(3, 4), False),
        (ints.closed_open(1, 3), ints.closed(4, 4), False),
        (ints.closed(3, 4), ints.closed_open(2, 3), False),
        (ints.closed(3, 4), ints.closed_open(1, 2), False),
        (ints.closed(3, 5), ints.singleton(4), True),
        (ints.closed_open(3, 5), ints.singleton(5), False),
        (ints.closed_open(3, 5), ints.at_least(5), False),
        (ints.closed(3, 5), ints.at_least(4), True),
        (ints.closed(3, 5), ints.at_least(2), True),
        (ints.unbounded(), ints.at_least(2), True),
    ],
)
@pytest.mark.nofilldb()
def test_overlaps(int1, int2: ints.Interval[int], expected: bool):
    assert expected == int1.overlaps(int2)


@pytest.mark.parametrize(
    'int1, int2, expected',
    [
        (ints.singleton(1), ints.singleton(1), ints.singleton(1)),
        (ints.singleton(1), ints.singleton(3), ints.closed(1, 3)),
        (ints.closed(1, 3), ints.closed(2, 4), ints.closed(1, 4)),
        (ints.closed(1, 3), ints.closed(3, 4), ints.closed(1, 4)),
        (ints.closed(2, 4), ints.closed(1, 3), ints.closed(1, 4)),
        (ints.closed(1, 5), ints.closed(5, 6), ints.closed(1, 6)),
        (ints.closed(2, 4), ints.closed(0, 5), ints.closed(0, 5)),
        (ints.closed(2, 8), ints.closed(3, 5), ints.closed(2, 8)),
        (ints.closed(2, 5), ints.closed(7, 9), ints.closed(2, 9)),
        (ints.closed(1, 3), ints.closed_open(2, 4), ints.closed_open(1, 4)),
        (ints.closed_open(1, 3), ints.closed(3, 4), ints.closed(1, 4)),
        (ints.closed_open(2, 4), ints.closed(1, 3), ints.closed_open(1, 4)),
        (ints.closed(1, 5), ints.closed_open(5, 6), ints.closed_open(1, 6)),
        (ints.closed(2, 4), ints.closed_open(0, 5), ints.closed_open(0, 5)),
        (ints.closed(2, 8), ints.closed_open(3, 5), ints.closed(2, 8)),
        (
            ints.closed_open(2, 5),
            ints.closed_open(7, 9),
            ints.closed_open(2, 9),
        ),
        (ints.unbounded(), ints.unbounded(), ints.unbounded()),
        (ints.unbounded(), ints.closed_open(7, 9), ints.unbounded()),
    ],
)
def test_span(int1, int2: ints.Interval[int], expected: bool):
    assert expected == int1.span(int2)


def test_map():
    assert ints.closed_open(10, 20) == ints.closed_open(5, 10).map(
        lambda x: x * 2,
    )


@pytest.mark.parametrize(
    'interval, expected',
    [
        (
            ints.interval(1, ints.BoundType.CLOSED, 5, ints.BoundType.CLOSED),
            ints.closed(1, 5),
        ),
        (
            ints.interval(1, ints.BoundType.CLOSED, 5, ints.BoundType.OPEN),
            ints.closed_open(1, 5),
        ),
    ],
)
def test_interval(interval: ints.Interval[int], expected: ints.Interval[int]):
    assert expected == interval


@pytest.mark.parametrize(
    'intervals, expected',
    [
        (
            [
                ints.closed(1, 3),
                ints.closed(5, 7),
                ints.closed(6, 8),
                ints.closed_open(9, 10),
                ints.closed_open(10, 11),
            ],
            [ints.closed(1, 3), ints.closed(5, 8), ints.closed_open(9, 11)],
        ),
    ],
)
def test_merge_connected(
        intervals: List[ints.Interval[int]],
        expected: List[ints.Interval[int]],
):
    assert expected == ints.merge_connected(intervals)
