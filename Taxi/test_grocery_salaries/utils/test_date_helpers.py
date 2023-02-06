import datetime as dt

import pytest

from grocery_salaries.utils.date_helpers import date_range_str
from grocery_salaries.utils.date_helpers import find_delta_in_weeks
from grocery_salaries.utils.date_helpers import is_week_delta_odd


@pytest.mark.parametrize(
    'start_date, end_date, result',
    [
        (dt.date(2021, 11, 15), dt.date(2021, 11, 30), 2),
        (dt.date(2021, 11, 15), dt.date(2021, 11, 23), 1),
        (dt.date(2021, 11, 1), dt.date(2021, 11, 9), 1),
        (dt.date(2021, 11, 2), dt.date(2021, 11, 9), 1),
        (dt.date(2021, 11, 1), dt.date(2021, 11, 27), 3),
        (dt.date(2021, 11, 29), dt.date(2021, 12, 7), 1),
        (dt.date(2021, 12, 27), dt.date(2022, 1, 4), 1),
        (dt.date(2020, 2, 24), dt.date(2020, 3, 9), 2),
        (dt.date(2021, 11, 15), dt.date(2021, 11, 22), 1),
        (dt.date(2021, 11, 15), dt.date(2021, 11, 21), 0),
        (dt.date(2021, 11, 15), dt.date(2021, 11, 20), 0),
        (dt.date(2021, 11, 15), dt.date(2021, 11, 30), 2),
        (dt.date(2021, 11, 15), dt.date(2021, 11, 7), -1),
    ],
)
def test_find_delta_in_weeks(
        start_date: dt.date, end_date: dt.date, result: int,
):
    delta = find_delta_in_weeks(start_date, end_date)

    assert delta == result


@pytest.mark.now('2021-11-23 00:00:00')
def test_skip_calculation_odd_week():
    biweekly_start_date = dt.date(year=2021, month=11, day=15)
    skip = is_week_delta_odd(biweekly_start_date, dt.date.today())
    assert skip is True


@pytest.mark.now('2021-11-30 00:00:00')
def test_skip_calculation_even_week():
    biweekly_start_date = dt.date(year=2021, month=11, day=15)
    skip = is_week_delta_odd(biweekly_start_date, dt.date.today())
    assert skip is False


@pytest.mark.now('2021-11-01 00:00:00')
def test_skip_calculation_calc_date_before_start_date():
    biweekly_start_date = dt.date(year=2021, month=11, day=15)
    skip = is_week_delta_odd(biweekly_start_date, dt.date.today())
    assert skip is True


def test_date_range_str():
    start_date = '2020-02-28'
    end_date = '2020-03-01'
    result = ['2020-02-28', '2020-02-29', '2020-03-01']
    assert date_range_str(start_date, end_date) == result
