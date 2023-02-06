import pytest
from datetime import date
from dmp_suite.market.recalculation import (
    last_day_of_month, first_day_of_month, UnitOfMeasurement, DateIntervalsSplitter, Segment
)


@pytest.mark.parametrize(
    'any_date, expected_date', [
        pytest.param('2021-01-17', '2021-01-31'),
        pytest.param('2021-02-28', '2021-02-28'),
        pytest.param('2021-03-01', '2021-03-31'),
        pytest.param('2020-02-05', '2020-02-29'),
    ]
)
def test__last_day_of_month(any_date, expected_date):
    actual = last_day_of_month(date.fromisoformat(any_date))
    expected = date.fromisoformat(expected_date)
    assert actual == expected


@pytest.mark.parametrize(
    'any_date, expected_date', [
        pytest.param('2021-01-17', '2021-01-01'),
        pytest.param('2021-02-28', '2021-02-01'),
        pytest.param('2021-03-01', '2021-03-01'),
    ]
)
def test__first_day_of_month(any_date, expected_date):
    actual = first_day_of_month(date.fromisoformat(any_date))
    expected = date.fromisoformat(expected_date)
    assert actual == expected


@pytest.mark.parametrize(
    'offset_string, expected_offset', [
        pytest.param(None, None),
        pytest.param('', None),
        pytest.param('1 day', None),
        pytest.param('1', UnitOfMeasurement(1, 'days')),
        pytest.param('2days', UnitOfMeasurement(2, 'days')),
        pytest.param('0 days', UnitOfMeasurement(0, 'days')),
        pytest.param('months', UnitOfMeasurement(0, 'months')),
        pytest.param('2 months', UnitOfMeasurement(2, 'months')),
        pytest.param('3months', UnitOfMeasurement(3, 'months')),
        pytest.param('months 3', None),
    ]
)
def test__offset_parse(offset_string, expected_offset):
    actual = UnitOfMeasurement.parse(offset_string)
    assert actual == expected_offset


@pytest.mark.parametrize(
    'quantity, unit, expected_exception', [
        pytest.param(1, None, ValueError),
        pytest.param(None, 'months', ValueError),
        pytest.param(-1, 'days', ValueError),
        pytest.param(10, 'day', ValueError),
    ]
)
def test__offset_init__fail_check(
        quantity, unit, expected_exception
):
    with pytest.raises(expected_exception):
        UnitOfMeasurement(quantity, unit)


@pytest.mark.parametrize(
    'quantity, unit, expected', [
        pytest.param(None, None, UnitOfMeasurement(0, 'days'))
    ]
)
def test__offset_init__none_values(
        quantity, unit, expected
):
    assert UnitOfMeasurement(quantity, unit) == expected


@pytest.mark.parametrize(
    'offset, interval, expected_exception', [
        pytest.param(UnitOfMeasurement(0, 'months'), UnitOfMeasurement(1, 'days'), ValueError),
        pytest.param(UnitOfMeasurement(10, 'days'), UnitOfMeasurement(10, 'days'), ValueError),
        pytest.param(UnitOfMeasurement(1, 'months'), UnitOfMeasurement(1, 'months'), ValueError),
        pytest.param(UnitOfMeasurement(56, 'days'), UnitOfMeasurement(2, 'months'), ValueError),
        pytest.param(UnitOfMeasurement(28, 'days'), UnitOfMeasurement(1, 'months'), ValueError),
    ]
)
def test__date_intervals_splitter__init__fail_validation(
        offset, interval, expected_exception
):
    with pytest.raises(expected_exception):
        DateIntervalsSplitter(offset, interval)


@pytest.mark.parametrize(
    'offset, interval, date_from, date_to, expected', [
        pytest.param(UnitOfMeasurement(0, 'days'), UnitOfMeasurement(1, 'days'), '2020-01-01', '2020-01-05',
                     [('2020-01-05', '2020-01-05'), ('2020-01-04', '2020-01-04'),
                      ('2020-01-03', '2020-01-03'), ('2020-01-02', '2020-01-02'),
                      ('2020-01-01', '2020-01-01')]),
        pytest.param(UnitOfMeasurement(0, 'days'), UnitOfMeasurement(2, 'days'), '2020-02-01', '2020-02-05',
                     [('2020-02-04', '2020-02-05'), ('2020-02-02', '2020-02-03'),
                      ('2020-02-01', '2020-02-01')]),
        pytest.param(UnitOfMeasurement(1, 'days'), UnitOfMeasurement(2, 'days'), '2020-03-01', '2020-03-05',
                     [('2020-03-05', '2020-03-05'), ('2020-03-02', '2020-03-03')]),
        pytest.param(UnitOfMeasurement(5, 'days'), UnitOfMeasurement(7, 'days'), '2020-03-28', '2020-04-05',
                     [('2020-04-02', '2020-04-05')]),
        pytest.param(UnitOfMeasurement(0, 'days'), UnitOfMeasurement(7, 'days'), '2020-01-01', '2020-01-05',
                     [('2020-01-01', '2020-01-05')]),
    ]
)
def test__date_intervals_splitter__offset_days_interval_days(
        offset, interval, date_from, date_to, expected
):
    splitter = DateIntervalsSplitter(offset, interval)
    actual = splitter.split(date.fromisoformat(date_from), date.fromisoformat(date_to))
    expected = [Segment(date.fromisoformat(l), date.fromisoformat(r)) for l, r in expected]
    assert actual == expected


@pytest.mark.parametrize(
    'offset, interval, date_from, date_to, expected', [
        pytest.param(UnitOfMeasurement(0, 'days'), UnitOfMeasurement(1, 'months'), '2020-01-01', '2020-01-05',
                     [('2020-01-01', '2020-01-05')]),
        pytest.param(UnitOfMeasurement(0, 'days'), UnitOfMeasurement(1, 'months'), '2020-01-25', '2020-03-05',
                     [('2020-03-01', '2020-03-05'), ('2020-02-01', '2020-02-29'),
                      ('2020-01-25', '2020-01-31')]),
        pytest.param(UnitOfMeasurement(5, 'days'), UnitOfMeasurement(1, 'months'), '2020-01-25', '2020-03-05',
                     [('2020-02-01', '2020-03-05'), ('2020-01-30', '2020-01-31')]),
        pytest.param(UnitOfMeasurement(7, 'days'), UnitOfMeasurement(1, 'months'), '2020-01-25', '2020-03-05',
                     [('2020-02-01', '2020-03-05')]),
        pytest.param(UnitOfMeasurement(5, 'days'), UnitOfMeasurement(1, 'months'), '2020-01-27', '2020-02-05',
                     [('2020-02-01', '2020-02-05')]),
    ]
)
def test__date_intervals_splitter__offset_days_interval_months(
        offset, interval, date_from, date_to, expected
):
    splitter = DateIntervalsSplitter(offset, interval)
    actual = splitter.split(date.fromisoformat(date_from), date.fromisoformat(date_to))
    expected = [Segment(date.fromisoformat(l), date.fromisoformat(r)) for l, r in expected]
    assert actual == expected


@pytest.mark.parametrize(
    'offset, interval, date_from, date_to, expected', [
        pytest.param(UnitOfMeasurement(0, 'months'), UnitOfMeasurement(1, 'months'), '2020-01-01', '2020-02-05',
                     [('2020-02-01', '2020-02-29'), ('2020-01-01', '2020-01-31')]),
        pytest.param(UnitOfMeasurement(0, 'months'), UnitOfMeasurement(6, 'months'), '2020-01-01', '2021-05-05',
                     [('2021-01-01', '2021-05-31'), ('2020-07-01', '2020-12-31'),
                      ('2020-01-01', '2020-06-30')]),
        pytest.param(UnitOfMeasurement(3, 'months'), UnitOfMeasurement(6, 'months'), '2020-01-01', '2021-05-05',
                     [('2021-04-01', '2021-05-31'), ('2020-10-01', '2020-12-31'),
                      ('2020-04-01', '2020-06-30')]),
    ]
)
def test__date_intervals_splitter__offset_months_interval_months(
        offset, interval, date_from, date_to, expected
):
    splitter = DateIntervalsSplitter(offset, interval)
    actual = splitter.split(date.fromisoformat(date_from), date.fromisoformat(date_to))
    expected = [Segment(date.fromisoformat(l), date.fromisoformat(r)) for l, r in expected]
    assert actual == expected
