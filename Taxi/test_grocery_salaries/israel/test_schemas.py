import datetime as dt

import pytest

from grocery_salaries.utils.date_helpers import is_weekend_israel


@pytest.mark.parametrize(
    'date, result',
    [
        (dt.date(2021, 11, 1), False),  # Mon
        (dt.date(2021, 11, 2), False),  # Tue
        (dt.date(2021, 11, 3), False),  # Wed
        (dt.date(2021, 11, 4), False),  # Thu
        (dt.date(2021, 11, 5), True),  # Fri
        (dt.date(2021, 11, 6), True),  # Sat
        (dt.date(2022, 11, 7), False),  # Sun
        (dt.date(2021, 9, 6), True),  # Holidays
        (dt.date(2021, 9, 7), True),
        (dt.date(2021, 9, 8), True),
    ],
)
def test_is_weekend_israel(date: dt.datetime, result: bool):
    assert is_weekend_israel(date) == result
