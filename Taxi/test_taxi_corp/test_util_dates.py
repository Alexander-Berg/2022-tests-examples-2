import datetime

import freezegun
import pytest

from taxi_corp.util import dates

_NOW = datetime.datetime(2019, 3, 19, 12, 40)


@pytest.mark.now(_NOW.isoformat())
def test_very_begin_of_curr_month():
    result = dates.very_beginning_of_current_month()
    assert result == datetime.datetime(2019, 3, 1, 0, 0)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'current_month', [1, 3],  # Jan -> Dec 1 last year  # Mar -> Feb 1
)
def test_very_begin_of_last_month(current_month):
    with freezegun.freeze_time(_NOW.replace(month=current_month)):
        result = dates.very_beginning_of_last_month()
        year = datetime.date.today().year
        if current_month == 1:
            last_month = 12
            year = year - 1
        else:
            last_month = current_month - 1
        assert result == datetime.datetime(year, last_month, 1, 0, 0)


@pytest.mark.now(_NOW.isoformat())
def test_very_end_of_day():
    result = dates.very_end_of_day(datetime.date(2019, 2, 1))
    assert result == datetime.datetime(2019, 2, 1, 23, 59, 59, 999999)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'current_month, last_day_of_last_month, year',
    [
        (1, 31, 2019),  # Jan -> Dec 31
        (3, 28, 2019),  # Mar -> Feb 28
        (3, 29, 2020),  # Mar -> Feb 29 == leap year
        (5, 30, 2020),  # May -> Apr 30
    ],
)
def test_very_end_of_last_month(current_month, last_day_of_last_month, year):
    with freezegun.freeze_time(_NOW.replace(month=current_month, year=year)):
        result = dates.very_end_of_last_month()
        if current_month == 1:
            last_month = 12
            year = year - 1
        else:
            last_month = current_month - 1
        assert result == datetime.datetime(
            year, last_month, last_day_of_last_month, 23, 59, 59, 999999,
        )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'current_month, current_day, yesterday_month, yesterday_day',
    [
        (1, 2, 1, 1),  # Jan 2 -> Jan 1
        (1, 1, 12, 31),  # Jan 1 -> Dec 31 last year
    ],
)
def test_very_end_of_yesterday(
        current_month, current_day, yesterday_month, yesterday_day,
):
    with freezegun.freeze_time(
            _NOW.replace(month=current_month, day=current_day),
    ):
        result = dates.very_end_of_yesterday()
        year = datetime.date.today().year
        if current_month == 1 and current_day == 1:
            year = year - 1

        assert result == datetime.datetime(
            year, yesterday_month, yesterday_day, 23, 59, 59, 999999,
        )
