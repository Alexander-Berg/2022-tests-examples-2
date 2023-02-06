import collections

import pytest

from stq_agent_py3.utils import percentile


def test_percentile_basic():
    counter = collections.Counter()
    counter[3] += 1
    assert percentile.get_percentile(counter, 100) == 3


def test_percentile_invalid_percent():
    counter = collections.Counter()
    counter[3] += 1
    with pytest.raises(ValueError):
        percentile.get_percentile(counter, -1)
    with pytest.raises(ValueError):
        percentile.get_percentile(counter, 101)


def test_percentile_no_accounts():
    counter = collections.Counter()
    assert percentile.get_percentile(counter, 100) == 0
    assert percentile.get_percentile(counter, 50) == 0
    assert percentile.get_percentile(counter, 1) == 0
    assert percentile.get_percentile(counter, 0) == 0


def test_percentile_calc_percentile_1():
    counter = collections.Counter()

    counter[10] += 1
    assert percentile.get_percentile(counter, 100) == 10
    assert percentile.get_percentile(counter, 98) == 10
    assert percentile.get_percentile(counter, 50) == 10
    assert percentile.get_percentile(counter, 1) == 10

    counter[20] += 1
    assert percentile.get_percentile(counter, 100) == 20
    assert percentile.get_percentile(counter, 51) == 20
    assert percentile.get_percentile(counter, 50) == 10
    assert percentile.get_percentile(counter, 1) == 10


def test_percentile_calc_percentile_2():
    counter = collections.Counter()

    for i in range(1, 101):
        counter[i] += 1

    for i in range(1, 101):
        assert percentile.get_percentile(counter, i) == i


def test_percentile_zero():
    counter = collections.Counter()

    counter[0] += 1
    assert percentile.get_percentile(counter, 100) == 0
    assert percentile.get_percentile(counter, 75) == 0
    assert percentile.get_percentile(counter, 50) == 0
    assert percentile.get_percentile(counter, 1) == 0

    counter[0] += 1
    counter[0] += 1
    counter[10] += 1
    assert percentile.get_percentile(counter, 100) == 10
    assert percentile.get_percentile(counter, 76) == 10
    assert percentile.get_percentile(counter, 75) == 0
    assert percentile.get_percentile(counter, 50) == 0
    assert percentile.get_percentile(counter, 1) == 0


def test_percentile_zero_percent_1():
    counter = collections.Counter()
    counter[49] += 1
    assert percentile.get_percentile(counter, 0) == 49
    counter[50] += 1
    assert percentile.get_percentile(counter, 0) == 49
    counter[100] += 1
    assert percentile.get_percentile(counter, 0) == 49
    counter[1] += 1
    assert percentile.get_percentile(counter, 0) == 1
    counter[0] += 1
    assert percentile.get_percentile(counter, 0) == 0


def test_percentile_multiple_account():
    counter = collections.Counter()
    for i in range(1, 5):
        counter[i] += i * 10

    assert percentile.get_percentile(counter, 10) == 1
    assert percentile.get_percentile(counter, 20) == 2
    assert percentile.get_percentile(counter, 30) == 2
    assert percentile.get_percentile(counter, 40) == 3
    assert percentile.get_percentile(counter, 60) == 3
    assert percentile.get_percentile(counter, 70) == 4


def test_percentile_multiple_percents():
    counter = collections.Counter()
    for i in range(1, 6):
        counter[i] += 1

    for (percent, value), (expected_percent, expected_value) in zip(
            percentile.get_percentiles(
                counter, (40, 20, 80, 60, 100, 61, 59, 41),
            ),
            (
                (20, 1),
                (40, 2),
                (41, 3),
                (59, 3),
                (60, 3),
                (61, 4),
                (80, 4),
                (100, 5),
            ),
    ):
        assert percent == expected_percent
        assert value == expected_value
