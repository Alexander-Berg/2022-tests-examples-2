import pytest

import dateutil.tz as tz
import pytz

from dmp_suite import datetime_utils as dtu
from datetime import datetime, timedelta, date

from dmp_suite.datetime_utils import DateWindow, Period, HourWindow
from dmp_suite.exceptions import DWHError


@pytest.mark.parametrize(
    'dttm_str, expected', [
        ('2017-03-03 02:00:00.777777', datetime(2017, 3, 3, 2, 0, 0, 777777)),
        ('2017-03-03 02:00:00.777', datetime(2017, 3, 3, 2, 0, 0, 777000)),
        ('2017-03-03 02:00:00,777777', datetime(2017, 3, 3, 2, 0, 0, 777777)),  # oktell uses this format
        (b'2017-03-03 02:00:00.777777', datetime(2017, 3, 3, 2, 0, 0, 777777)),
        ('2017-03-03T02:00:00.777777+02:25', datetime(2017, 3, 2, 23, 35, 0, 777777)),
        ('2017-03-03 02:00:00.777777+00:00кря-кря', datetime(2017, 3, 3, 2, 0, 0, 777777)),
        ('2017-03-03 02:00:00.777777Z', datetime(2017, 3, 3, 2, 0, 0, 777777)),
        ('2016-09-27T16:01:33+00:00', datetime(2016, 9, 27, 16, 1, 33)),
        ('2016-09-27T16:01:33.012345+00:00', datetime(2016, 9, 27, 16, 1, 33, 12345)),
        ('2017-03-03Z', datetime(2017, 3, 3)),
        ('2017-03-03', datetime(2017, 3, 3)),
        ('2017-04-03T07:09:00', datetime(2017, 4, 3, 7, 9)),
        ('2017-03', datetime(2017, 3, 1)),
        ('2017', datetime(2017, 1, 1)),
    ]
)
def test_parse_datetime(dttm_str, expected):
    assert dtu.parse_datetime(dttm_str) == expected


@pytest.mark.parametrize(
    'dttm_str, expected', [
        ('2017-03-03 02:00:00.777777', datetime(2017, 3, 3)),
        (b'2017-03-03 02:00:00.777777', datetime(2017, 3, 3)),
        ('2017-03-03T02-00-00.777777+02:25', datetime(2017, 3, 3)),
        ('2017-03-03', datetime(2017, 3, 3)),
        ('2017-04-03T07:09:00', datetime(2017, 4, 3)),
    ]
)
def test_parse_date(dttm_str, expected):
    assert dtu.parse_date(dttm_str) == expected


@pytest.mark.parametrize(
    'dttm_str', [
        '2017-03',
        '2017',
    ]
)
def test_parse_date_raises(dttm_str):
    with pytest.raises(ValueError):
        dtu.parse_date(dttm_str)


@pytest.mark.parametrize(
    'value, expected', [
        ('2017-03-03 02:00:00.777777', '2017-03-03 02:00:00.777777'),
        ('2017-03-03T02:00:00.777777Z', '2017-03-03 02:00:00.777777'),
        ('2017-03-03', '2017-03-03 00:00:00.000000'),
        (datetime(2017, 3, 6), '2017-03-06 00:00:00.000000'),
        (datetime(1097, 3, 6), '1097-03-06 00:00:00.000000'),
    ]
)
def test_format_datetime_microseconds(value, expected):
    assert dtu.format_datetime_microseconds(value) == expected


@pytest.mark.parametrize(
    'value, expected', [
        ('2017-03-03 02:00:00.777777', '2017-03-03 02:00:00'),
        ('2017-03-03T02:00:00.777777Z', '2017-03-03 02:00:00'),
        ('2017-03-03', '2017-03-03 00:00:00'),
        (datetime(2017, 3, 6), '2017-03-06 00:00:00'),
        (datetime(1097, 3, 6), '1097-03-06 00:00:00'),
        (date(1097, 3, 6), '1097-03-06 00:00:00'),
    ]
)
def test_format_datetime(value, expected):
    assert dtu.format_datetime(value) == expected


@pytest.mark.parametrize(
    'value, expected', [
        ('2017-03-03 02:00:00.777777', '2017-03-03 02:00:00'),
        ('2017-03-03 02:00:00Z', '2017-03-03 02:00:00'),
        ('2017-03-03T02:00:00.777777Z', '2017-03-03 02:00:00'),
        ('2017-03-03T02:00:00Z', '2017-03-03 02:00:00'),
        ('2017-03-03T07:00:00+03:00', '2017-03-03 04:00:00'),
        ('2017-03-03', '2017-03-03 00:00:00'),
        (datetime(2017, 3, 6), '2017-03-06 00:00:00'),
        (datetime(1097, 3, 6), '1097-03-06 00:00:00'),
        (date(1097, 3, 6), '1097-03-06 00:00:00'),
    ]
)
def test_correct_format_datetime(value, expected):
    assert dtu.correct_format_datetime(value) == expected


@pytest.mark.parametrize(
    'value, expected', [
        ('2017-03-03 02:00:00.777777', '2017-03-03'),
        ('2017-03-03 02:00:00.777777Z', '2017-03-03'),
        ('2017-03-03', '2017-03-03'),
        (datetime(2017, 3, 6), '2017-03-06'),
        (datetime(1097, 3, 6), '1097-03-06'),
    ]
)
def test_format_date(value, expected):
    assert dtu.format_date(value) == expected


@pytest.mark.parametrize(
    'value, expected', [
        ('2017-03-03 02:00:00.777777', '2017-03'),
        ('2017-03-03 02:00:00.777777Z', '2017-03'),
        ('2017-03-03', '2017-03'),
        (datetime(2017, 3, 6), '2017-03'),
        (datetime(1097, 3, 6), '1097-03'),
        ('2017-03', '2017-03'),
    ]
)
def test_format_month(value, expected):
    assert dtu.format_month(value) == expected


@pytest.mark.parametrize(
    'value, expected', [
        ('2017-03-03 02:00:00.777777', '2017'),
        ('2017-03-03 02:00:00.777777Z', '2017'),
        ('2017-03-03', '2017'),
        (datetime(2017, 3, 6), '2017'),
        (datetime(1097, 3, 6), '1097'),
        ('2017-03', '2017'),
    ]
)
def test_format_year(value, expected):
    assert dtu.format_year(value) == expected


@pytest.mark.parametrize(
    'formatter, value', [
        (dtu.format_datetime_microseconds, '2017-0'),
        (dtu.format_datetime, '2017-0'),
        (dtu.format_date, '2017-0'),
        (dtu.format_month, '201703'),
        (dtu.format_year, '201'),
    ]
)
def test_format_raises(formatter, value):
    with pytest.raises(ValueError):
        formatter(value)


def test_validate_format():
    with pytest.raises(ValueError):
        dtu.validate_format('2020-04-20', dtu.DATE_TIME_FORMAT)

    dtu.validate_format('2020-04-20', dtu.DATE_FORMAT)

    with pytest.raises(ValueError):
        dtu.validate_format('2020-04-20 12:34:45', dtu.DATE_FORMAT)

    dtu.validate_format('2020-04-20 12:34:45', dtu.DATE_TIME_FORMAT)

    with pytest.raises(TypeError):
        dtu.validate_format(datetime(2020, 4, 20), dtu.DATE_FORMAT)

    with pytest.raises(TypeError):
        dtu.validate_format(datetime(2020, 4, 20, 23, 59, 59), dtu.DATE_FORMAT)


def test_period():
    with pytest.raises(ValueError):
        dtu.Period('2017-03-01', '2016-03-11')

    p1 = dtu.period(datetime(2017, 2, 27), datetime(2017, 3, 2))
    p2 = dtu.period(datetime(2017, 2, 27), datetime(2017, 3, 2))
    assert p1 == p2

    p2 = dtu.period(datetime(2017, 2, 27), datetime(2017, 3, 1))
    assert not p1 == p2


def test_period_split_in_month_periods():
    p = dtu.period(datetime(2017, 2, 27), datetime(2017, 3, 2))
    expected = [
        dtu.Period(datetime(2017, 2, 27),
                   datetime(2017, 2, 28, 23, 59, 59, 999999)),
        dtu.Period(datetime(2017, 3, 1), datetime(2017, 3, 2))
    ]
    actual = list(p.split_in_month_periods())
    assert expected == actual

    p = dtu.period(datetime(2017, 1, 27), datetime(2017, 3, 2))
    expected = [
        dtu.Period(datetime(2017, 1, 27),
                   datetime(2017, 1, 31, 23, 59, 59, 999999)),
        dtu.Period(datetime(2017, 2, 1),
                   datetime(2017, 2, 28, 23, 59, 59, 999999)),
        dtu.Period(datetime(2017, 3, 1), datetime(2017, 3, 2)),
    ]
    actual = list(p.split_in_month_periods())
    assert expected == actual

    p = dtu.period(datetime(2017, 1, 27), datetime(2017, 1, 30))
    expected = [dtu.Period(datetime(2017, 1, 27), datetime(2017, 1, 30))]
    actual = list(p.split_in_month_periods())
    assert expected == actual


def test_split_in_year_periods():
    d1 = '2010-01-07 12:30:30'
    d2 = '2011-12-30 12:13:30'
    middle1 = '2010-12-31 23:59:59.999999'
    middle2 = '2011-01-01 00:00:00'
    p = dtu.Period(d1, d2)
    assert list(p.split_in_year_periods()) == \
           [dtu.Period(d1, middle1), dtu.Period(middle2, d2)]


def test_extremum_overflow():
    # MAX_DATETIME ("9999-12-31 23:59:59") is not actually the maximal one.
    # get_end_of_day(MAX_DATETIME) == "9999-12-31 23:59:59.999999" is.
    p = dtu.Period('9998-12-01', dtu.get_end_of_day(dtu.MAX_DATETIME))
    list(p.split_in_days())
    list(p.split_in_hours())
    list(p.split_in_day_periods())
    list(p.split_in_hour_periods())
    list(p.split_in_week_periods())
    list(p.split_in_month_periods())
    list(p.split_in_year_periods())
    p = dtu.Period(dtu.MIN_DATETIME, '1972-04-01')
    list(p.split_in_days())
    list(p.split_in_hours())
    list(p.split_in_day_periods())
    list(p.split_in_month_periods())
    list(p.split_in_hour_periods())
    list(p.split_in_week_periods())
    list(p.split_in_year_periods())


def test_period_split_in_5_mins():
    p = dtu.period(
        datetime(2020, 1, 12, 4, 6, 10),
        datetime(2020, 1, 12, 4, 20, 5),
    )
    expected = [
        datetime(2020, 1, 12, 4, 5),
        datetime(2020, 1, 12, 4, 10),
        datetime(2020, 1, 12, 4, 15),
        datetime(2020, 1, 12, 4, 20),
    ]
    actual = list(p.split_in_5mins())
    assert expected == actual


def test_period_split_in_5_mins_periods():
    p = dtu.period(
        datetime(2020, 1, 12, 4, 6, 10),
        datetime(2020, 1, 12, 4, 20, 5),
    )
    expected = [
        dtu.period('2020-01-12 04:06:10', '2020-01-12 04:09:59.999999'),
        dtu.period('2020-01-12 04:10:00', '2020-01-12 04:14:59.999999'),
        dtu.period('2020-01-12 04:15:00', '2020-01-12 04:19:59.999999'),
        dtu.period('2020-01-12 04:20:00', '2020-01-12 04:20:05'),
    ]
    actual = list(p.split_in_5min_periods())
    assert expected == actual


def test_period_split_in_halfhours():
    p = dtu.period(
        datetime(2017, 2, 26, 23, 11),
        datetime(2017, 2, 27, 1, 23)
    )
    expected = [
        datetime(2017, 2, 26, 23),
        datetime(2017, 2, 26, 23, 30),
        datetime(2017, 2, 27, 0),
        datetime(2017, 2, 27, 0, 30),
        datetime(2017, 2, 27, 1)
    ]
    actual = list(p.split_in_halfhours())
    assert expected == actual


def test_period_split_in_halfhour_periods():
    p = dtu.period('2017-02-26 23:05:00', '2017-02-27 00:40:00')
    expected = [
        dtu.period('2017-02-26 23:05:00', '2017-02-26 23:29:59.999999'),
        dtu.period('2017-02-26 23:30:00', '2017-02-26 23:59:59.999999'),
        dtu.period('2017-02-27 00:00:00', '2017-02-27 00:29:59.999999'),
        dtu.period('2017-02-27 00:30:00', '2017-02-27 00:40:00')
    ]
    actual = list(p.split_in_halfhour_periods())
    assert expected == actual


def test_period_split_in_hours():
    p = dtu.period(
        datetime(2017, 2, 26, 23, 11),
        datetime(2017, 2, 27, 2, 23)
    )
    expected = [
        datetime(2017, 2, 26, 23),
        datetime(2017, 2, 27, 0),
        datetime(2017, 2, 27, 1),
        datetime(2017, 2, 27, 2)
    ]
    actual = list(p.split_in_hours())
    assert expected == actual


def test_period_split_in_days():
    p = dtu.period(datetime(2017, 2, 27), datetime(2017, 3, 2))
    expected = [
        datetime(2017, 2, 27),
        datetime(2017, 2, 28),
        datetime(2017, 3, 1),
        datetime(2017, 3, 2)
    ]
    actual = list(p.split_in_days())
    assert expected == actual


def test_period_split_in_months():
    p = dtu.period(datetime(2017, 2, 27), datetime(2017, 3, 2))
    expected = [
        datetime(2017, 2, 1),
        datetime(2017, 3, 1),
    ]
    actual = list(p.split_in_months())
    assert expected == actual


def test_split_in_day_periods():
    p = dtu.Period(datetime(2017, 2, 28), datetime(2017, 3, 1, 8))
    expected = [
        dtu.Period(datetime(2017, 2, 28), datetime(2017, 2, 28, 23, 59, 59, 999999)),
        dtu.Period(datetime(2017, 3, 1), datetime(2017, 3, 1, 8))
    ]
    actual = list(p.split_in_day_periods())
    assert expected == actual

    p = dtu.Period(datetime(2017, 2, 28), datetime(2017, 2, 28, 8))
    expected = [dtu.Period(datetime(2017, 2, 28), datetime(2017, 2, 28, 8)),]
    actual = list(p.split_in_day_periods())
    assert expected == actual

    p = dtu.Period(datetime(2017, 2, 28), datetime(2017, 2, 28))
    expected = [dtu.Period(datetime(2017, 2, 28), datetime(2017, 2, 28)),]
    actual = list(p.split_in_day_periods())
    assert expected == actual

    p = dtu.Period(datetime(2017, 2, 28, 7), datetime(2017, 2, 28, 8))
    expected = [dtu.Period(datetime(2017, 2, 28, 7), datetime(2017, 2, 28, 8)),]
    actual = list(p.split_in_day_periods())
    assert expected == actual

    p = dtu.Period('2018-05-21 10:00:00', '2018-05-22 10:00:00')
    expected = [
        dtu.Period(datetime(2018, 5, 21, 10), datetime(2018, 5, 21, 23, 59, 59, 999999)),
        dtu.Period(datetime(2018, 5, 22), datetime(2018, 5, 22, 10)),
    ]
    actual = list(p.split_in_day_periods())
    assert expected == actual


def test_period_within_calendar_month():
    assert not dtu.Period('2016-03-01', '2017-03-11').within_calendar_month


def test_period_within_calendar_day():
    assert not dtu.Period('2016-03-01', '2017-03-11').within_calendar_day


def test_period_equals():
    assert dtu.Period('2016-03-01', '2016-03-01') == dtu.Period('2016-03-01', '2016-03-01')
    assert dtu.Period('2016-03-01', '2016-03-11') == dtu.Period('2016-03-01', '2016-03-11')


@pytest.mark.parametrize(
    'func, expected', [
        (dtu.get_start_of_5min, datetime(2017, 2, 15, 13, 45, 0)),
        (dtu.get_start_of_halfhour, datetime(2017, 2, 15, 13, 30, 0)),
        (dtu.get_start_of_hour, datetime(2017, 2, 15, 13, 0, 0)),
        (dtu.get_start_of_day, datetime(2017, 2, 15, 0, 0, 0)),
        (dtu.get_start_of_week, datetime(2017, 2, 13, 0, 0, 0)),
        (dtu.get_start_of_month, datetime(2017, 2, 1, 0, 0, 0)),
        (dtu.get_start_of_year, datetime(2017, 1, 1, 0, 0, 0)),
    ]
)
@pytest.mark.parametrize(
    'tz', [None, dtu.MSK, dtu.UTC]
)
def test_start_of_dttm(func, expected, tz):
    assert func(datetime(2017, 2, 15, 13, 45, 30, tzinfo=tz)) == expected.replace(tzinfo=tz)


@pytest.mark.parametrize(
    'func, expected', [
        (dtu.get_end_of_5min, datetime(2017, 2, 15, 13, 19, 59, 999999)),
        (dtu.get_end_of_halfhour, datetime(2017, 2, 15, 13, 29, 59, 999999)),
        (dtu.get_end_of_hour, datetime(2017, 2, 15, 13, 59, 59, 999999)),
        (dtu.get_end_of_day, datetime(2017, 2, 15, 23, 59, 59, 999999)),
        (dtu.get_end_of_week, datetime(2017, 2, 19, 23, 59, 59, 999999)),
        (dtu.get_end_of_month, datetime(2017, 2, 28, 23, 59, 59, 999999)),
        (dtu.get_end_of_year, datetime(2017, 12, 31, 23, 59, 59, 999999)),
    ]
)
@pytest.mark.parametrize(
    'tz', [None, dtu.MSK, dtu.UTC]
)
def test_end_of_dttm(func, expected, tz):
    assert func(datetime(2017, 2, 15, 13, 15, 30, tzinfo=tz)) == expected.replace(tzinfo=tz)


def test_split_tz_period_into_periods_possible():
    period = dtu.Period(
        datetime(2005, 1, 23, tzinfo=dtu.MSK),
        datetime(2007, 1, 23, tzinfo=dtu.MSK)
    )
    list(period.split_in_day_periods())
    list(period.split_in_week_periods())
    list(period.split_in_month_periods())
    list(period.split_in_year_periods())
    list(period.split_in_hour_periods())
    list(period.split_in_days())
    list(period.split_in_hours())


def test_edges_of_year():
    some_dttm = '1987-08-01 21:30:00'
    assert dtu.get_end_of_year(some_dttm) == \
           datetime(year=1987, month=12, day=31,
                    hour=23, minute=59, second=59, microsecond=999999)
    assert dtu.get_start_of_year(some_dttm) == \
           datetime(year=1987, month=1, day=1,
                    hour=0, minute=0, second=0, microsecond=0)


@pytest.mark.parametrize(
    'tz', [None, dtu.MSK, dtu.UTC]
)
def test_period_split_in_month_periods_with_tz(tz):
    period = dtu.period(
        start=datetime(2017, 1, 5, tzinfo=tz),
        end=datetime(2017, 3, 5, tzinfo=tz),
    )
    actual = list(period.split_in_month_periods())
    expected = [
        dtu.Period(
            datetime(2017, 1, 5, tzinfo=tz),
            datetime(2017, 1, 31, 23, 59, 59, 999999, tzinfo=tz)
        ),
        dtu.Period(
            datetime(2017, 2, 1, tzinfo=tz),
            datetime(2017, 2, 28, 23, 59, 59, 999999, tzinfo=tz)
        ),
        dtu.Period(
            datetime(2017, 3, 1, tzinfo=tz),
            datetime(2017, 3, 5, tzinfo=tz)
        )
    ]
    assert actual == expected


def test_period_raises_with_tzinfo_in_one_dttm():
    with pytest.raises(TypeError):
        dtu.period(
            datetime(2017, 1, 5, tzinfo=dtu.UTC),
            datetime(2017, 3, 5),
        )
    with pytest.raises(TypeError):
        dtu.period(
            datetime(2017, 1, 5),
            datetime(2017, 3, 5, tzinfo=dtu.UTC),
        )


def test_contains():
    period = dtu.Period('2016-03-01', '2017-03-11')
    assert period.contains('2016-03-01')
    assert period.contains(dtu.datetime(year=2017, month=1, day=4, hour=3))
    assert period.contains('2017-02-11')
    assert period.contains('2017-02-11 12:12:12.123456')
    with pytest.raises(ValueError):
        period.contains('2017-02-11 12:12:12.1234')

    assert period.contains('2017-03-11')
    assert not period.contains('2018-03-11')

    p = dtu.Period('2017-05', '2017-06')
    assert '2017-05-04' in p
    assert '2017-05-04 12:12:12' in p

    p = dtu.Period('2017-05-01 12:12:12', '2017-07-02 12:12:12')
    assert '2017-06-01' in p
    assert '2017-06' in p


def test_contains_period():
    period = dtu.Period('2016-03-01', '2017-03-11')

    assert period.contains_period(period)
    assert period.contains_period(dtu.Period('2016-03-01 00:00:00', '2017-03-11 00:00:00'))
    assert not period.contains_period(dtu.Period('2016-02-29 23:59:59.999999', '2017-03-11 00:00:00'))
    assert not period.contains_period(dtu.Period('2016-03-01 00:00:00', '2017-03-11 00:00:01'))

    period = dtu.Period('2016-03-05 00:00:00.000000', '2016-03-05 00:00:00.000000')
    assert period.contains_period(period)


def test_intersects():
    p1 = dtu.Period('2015-01-01', '2017-01-01')
    assert p1.intersects(p1)
    p2 = dtu.Period('2016-01-01', '2019-01-01')
    assert p1.intersects(p2)
    assert p2.intersects(p1)
    p3 = dtu.Period('2015-05-01', '2015-06-01')
    assert p1.intersects(p3)
    assert p3.intersects(p1)


def test_intersection():
    p1 = dtu.Period('2015-01-01', '2017-01-01')
    assert p1.intersection(p1) == p1
    p2 = dtu.Period('2016-01-01', '2019-01-01')
    assert p1.intersection(p2) == dtu.Period('2016-01-01', '2017-01-01')
    assert p2.intersection(p1) == dtu.Period('2016-01-01', '2017-01-01')
    p3 = dtu.Period('2015-05-01', '2015-06-01')
    assert p1.intersection(p3) == p3
    assert p3.intersection(p1) == p3

    with pytest.raises(ValueError):
        p2.intersection(p3)
    with pytest.raises(ValueError):
        p3.intersection(p2)


def test_period_shift():
    p1 = dtu.Period('2020-04-15 11:00:00', '2020-04-15 12:00:00')
    p2 = p1.add_offset(timedelta(hours=3, minutes=30))
    p3 = dtu.Period('2020-04-15 14:30:00', '2020-04-15 15:30:00')
    assert p2 == p3


def test_window():
    dttm = dtu.parse_datetime('2017-04-12 12:34:43')

    period = dtu.Window() \
        .start(minutes=-2) \
        .end(hours=8) \
        .apply(dttm)

    assert period.start == dtu.parse_datetime('2017-04-12 12:32:43')
    assert period.end == dtu.parse_datetime('2017-04-12 20:34:43')

    period = dtu.Window() \
        .offset(minutes=-1) \
        .start(minutes=-2) \
        .apply(dttm)

    assert period.start == dtu.parse_datetime('2017-04-12 12:31:43')
    assert period.end == dtu.parse_datetime('2017-04-12 12:33:43')

    period = (
        dtu.Window()
            .replace(second=0)
            .start(minutes=-2)
            .end(hours=8)
            .apply(dttm)
        )

    assert period.start == dtu.parse_datetime('2017-04-12 12:32:00')
    assert period.end == dtu.parse_datetime('2017-04-12 20:34:00')

    window = dtu.Window()
    window.start.replace(second=50).offset(hours=-1)
    window.end.replace(minute=10)
    period = window.replace(minute=0, second=0).apply(dttm)

    assert period.start == dtu.parse_datetime('2017-04-12 11:00:50')
    assert period.end == dtu.parse_datetime('2017-04-12 12:10:00')

    window = dtu.Window()
    window.base.replace(minute=0, second=0).offset(days=-10)
    window.start(days=-1, hours=6)
    window.end.replace(hour=23, minute=59, second=59)
    period = window.apply(dttm)

    assert period.start == dtu.parse_datetime('2017-04-01 18:00:00')
    assert period.end == dtu.parse_datetime('2017-04-02 23:59:59')

    window = dtu.Window()
    window.start.offset(days=-60).transform(dtu.get_start_of_month)
    window.end.transform(dtu.get_start_of_month).offset(days=10)
    period = window.apply(dttm)

    assert period.start == dtu.parse_datetime('2017-02-01 00:00:00')
    assert period.end == dtu.parse_datetime('2017-04-11 00:00:00')


def test_str_time_interval_constructors():
    period = dtu.Period('2017-03-02', '2017-04-02 12:34:56')
    frozen_period_one = dtu.StringTimeInterval.from_period(period)
    frozen_period_two = dtu.StringTimeInterval(
        '2017-03-02', '2017-04-02 12:34:56')

    assert frozen_period_one._start == '2017-03-02 00:00:00.000000'
    assert frozen_period_two._start == '2017-03-02 00:00:00.000000'

    assert frozen_period_one._end == '2017-04-02 12:34:56.000000'
    assert frozen_period_two._end == '2017-04-02 12:34:56.000000'

    with pytest.raises(ValueError):
        dtu.StringTimeInterval('2017-04-02 12:34', '2017-04-02 12:34')

    assert frozen_period_one == frozen_period_one
    assert frozen_period_one == frozen_period_two


def test_str_time_interval_contains():
    fp = dtu.StringTimeInterval('2017-03-02', '2017-04-02 12:34:56')
    assert '2017-03-02' in fp
    assert '2017-03-02 12:12:12' in fp
    assert '2017-03-02 12:12:12.123456' in fp
    assert '2017-04-02 12:34:56' in fp

    assert '2017-04-02 12:34:56.000001' not in fp
    assert datetime(2017, 3, 3) in fp
    assert datetime(2017, 5, 5) not in fp

    fp = dtu.StringTimeInterval('2017-03-02', '2017-04-02 12:34:56',
                                closed='none')
    assert '2017-03-02' not in fp
    assert '2017-04-02 12:34:56' not in fp

    fp = dtu.StringTimeInterval('2017-03-02', '2017-04-02 12:34:56',
                                closed='left')
    assert '2017-03-02' in fp
    assert '2017-04-02 12:34:56' not in fp

    fp = dtu.StringTimeInterval('2017-03-02', '2017-04-02 12:34:56',
                                closed='right')
    assert '2017-03-02' not in fp
    assert '2017-04-02 12:34:56' in fp

    fp = dtu.StringTimeInterval('2017-01', '2017-02')
    assert '2017-01-05' in fp


@pytest.mark.parametrize(
    'value', ['123', '', None]
)
def test_validate_timezone(value):
    dtu.validate_timezone('Europe/Moscow')
    with pytest.raises(DWHError):
        dtu.validate_timezone(value)


@pytest.mark.parametrize(
    'dttm_str, expected', [
        ('2018-01-01T00:00:00', '2018-01-01 00:00:00'),
        ('2018-01-01T00:00:00TTT', '2018-01-01 00:00:00TTT'),
        ('2018-01-01', '2018-01-01'),
        (b'2018-01-01T00:00:00', b'2018-01-01 00:00:00'),
        (b'2018-01-01T00:00:00TTT', b'2018-01-01 00:00:00TTT'),
        (b'2018-01-01', b'2018-01-01'),
    ]
)
def test_iso_string_space_delimiter(dttm_str, expected):
    assert dtu.iso_string_space_delimiter(dttm_str) == expected


def test_msk_utc():
    assert dtu.msk2utc('2019-05-21 14:00:02') == datetime(
        2019, 5, 21, 11, 0, 2, tzinfo=dtu.UTC)

    assert dtu.utc2msk('2019-05-21 14:00:02') == datetime(
        2019, 5, 21, 14, 0, 2, tzinfo=dtu.UTC).astimezone(dtu.MSK)

    assert dtu.msk2utc_dttm('2019-05-21 14:00:02') == '2019-05-21 11:00:02'

    assert dtu.utc2msk_dttm('2019-05-21 14:00:02') == '2019-05-21 17:00:02'


def test_utc2local():
    assert dtu.utc2local('2019-05-21 14:00:02', dtu.MSK) == datetime(2019, 5, 21, 17, 0, 2)
    assert dtu.utc2local(datetime(2019, 5, 21, 14, 0, 2), dtu.MSK) == datetime(2019, 5, 21, 17, 0, 2)

    assert dtu.utc2local('2019-05-21 14:00:02', dtu.UTC) == datetime(2019, 5, 21, 14, 0, 2)
    assert dtu.utc2local(datetime(2019, 5, 21, 14, 0, 2), dtu.UTC) == datetime(2019, 5, 21, 14, 0, 2)

    assert dtu.utc2local('2019-05-21 14:00:02', 'Europe/Moscow') == datetime(2019, 5, 21, 17, 0, 2)
    assert dtu.utc2local(datetime(2019, 5, 21, 14, 0, 2), 'Europe/Moscow') == datetime(2019, 5, 21, 17, 0, 2)

    assert dtu.utc2local('2019-05-21 14:00:02', 'UTC') == datetime(2019, 5, 21, 14, 0, 2)
    assert dtu.utc2local(datetime(2019, 5, 21, 14, 0, 2), 'UTC') == datetime(2019, 5, 21, 14, 0, 2)


def test_split_into_periods():
    # split into 5 second periods
    get_period_end = lambda dttm: dttm + timedelta(seconds=5, microseconds=-1)
    expected = [
        dtu.period('2018-01-01 05:05:05', '2018-01-01 05:05:09.999999'),
        dtu.period('2018-01-01 05:05:10', '2018-01-01 05:05:14.999999'),
        dtu.period('2018-01-01 05:05:15', '2018-01-01 05:05:19.999999'),
        dtu.period('2018-01-01 05:05:20', '2018-01-01 05:05:21')
    ]
    period = dtu.period('2018-01-01 05:05:05', '2018-01-01 05:05:21')
    assert expected == list(period.split_into_periods(get_period_end))

    # to small period for split
    expected = [dtu.period('2018-01-01 05:05:05', '2018-01-01 05:05:06')]
    period = dtu.period('2018-01-01 05:05:05', '2018-01-01 05:05:06')
    assert expected == list(period.split_into_periods(get_period_end))

    # split in minutes similar to dtu.get_start_of_... functions
    get_period_end = lambda dttm: (
        dttm.replace(second=0, microsecond=0)
        + timedelta(minutes=1, microseconds=-1)
    )
    expected = [
        dtu.period('2018-01-01 05:05:05', '2018-01-01 05:05:59.999999'),
        dtu.period('2018-01-01 05:06:00', '2018-01-01 05:06:59.999999'),
        dtu.period('2018-01-01 05:07:00', '2018-01-01 05:07:21')
    ]
    period = dtu.period('2018-01-01 05:05:05', '2018-01-01 05:07:21')
    assert expected == list(period.split_into_periods(get_period_end))

    # test overflow
    get_period_end = lambda dttm: dttm + timedelta(hours=1)
    period = dtu.period('9999-12-31 23:59:50', '9999-12-31 23:59:55')
    expected = [period]
    assert expected == list(period.split_into_periods(get_period_end))


@pytest.mark.parametrize(
    "given_period, given_args, given_kwargs, expect",
    [
        # Test accepts timedelta.
        [
            dtu.date_period("2020-01-03", "2020-01-07"),
            [timedelta(days=3)],
            {},
            [
                dtu.date_period("2020-01-03", "2020-01-05"),
                dtu.date_period("2020-01-06", "2020-01-07"),
            ],
        ],
        # Test passes arguments to timedelta.
        [
            dtu.date_period("2020-01-03", "2020-01-07"),
            [],
            {"days": 3},
            [
                dtu.date_period("2020-01-03", "2020-01-05"),
                dtu.date_period("2020-01-06", "2020-01-07"),
            ],
        ],
        # Test behaves well when the period equals timedela.
        [
            dtu.date_period("2020-01-03", "2020-01-07"),
            [],
            {"days": 5},
            [dtu.date_period("2020-01-03", "2020-01-07")],
        ],
        # Test behaves well when the period is less than timedela.
        [
            dtu.date_period("2020-01-03", "2020-01-07"),
            [],
            {"days": 7},
            [dtu.date_period("2020-01-03", "2020-01-07")],
        ],
        # Test works well with MAX_DATE.
        [
            dtu.date_period("9999-12-31", "9999-12-31"),
            [],
            {"days": 7},
            [dtu.date_period("9999-12-31", "9999-12-31")],
        ],
    ],
)
def test_split_in_equal_periods(given_period, given_args, given_kwargs, expect):
    assert (
        list(given_period.split_in_equal_periods(*given_args, **given_kwargs)) == expect
    )


@pytest.mark.parametrize(
    "given_datetime, expect_before, expect_after",
    [
        (
            dtu.parse_datetime('2018-01-01 05:05:25'),
            dtu.period('2018-01-01 05:05:20', '2018-01-01 05:05:24.999999'),
            dtu.period('2018-01-01 05:05:25', '2018-01-02 05:35:21.999999'),
        ),
        (
            '2018-01-01 05:05:19',
            None,
            dtu.period('2018-01-01 05:05:20', '2018-01-02 05:35:21.999999'),
        ),
        (
            '2018-01-01 05:05:20',
            None,
            dtu.period('2018-01-01 05:05:20', '2018-01-02 05:35:21.999999'),
        ),
        (
            '2018-01-01 05:05:20.000001',
            dtu.period('2018-01-01 05:05:20', '2018-01-01 05:05:20'),
            dtu.period('2018-01-01 05:05:20.000001', '2018-01-02 05:35:21.999999'),
        ),
        (
            '2018-01-01 05:05:25',
            dtu.period('2018-01-01 05:05:20', '2018-01-01 05:05:24.999999'),
            dtu.period('2018-01-01 05:05:25', '2018-01-02 05:35:21.999999'),
        ),
        (
            '2018-01-02 05:35:21.999999',
            dtu.period('2018-01-01 05:05:20', '2018-01-02 05:35:21.999998'),
            dtu.period('2018-01-02 05:35:21.999999', '2018-01-02 05:35:21.999999'),
        ),
        (
            '2018-01-02 05:35:22',
            dtu.period('2018-01-01 05:05:20', '2018-01-02 05:35:21.999999'),
            None,
        ),
        (
            '2018-01-02 05:35:23',
            dtu.period('2018-01-01 05:05:20', '2018-01-02 05:35:21.999999'),
            None,
        ),
    ]
)
def test_split_by_datetime(given_datetime, expect_before, expect_after):
    given_period = dtu.period('2018-01-01 05:05:20', '2018-01-02 05:35:21.999999')
    before, after = given_period.split_by_datetime(given_datetime)
    assert (expect_before, expect_after) == (before, after)


def test_parse_time_delta():
    assert dtu.parse_time_delta("25hours") == timedelta(1, 3600)
    assert dtu.parse_time_delta("30days 25hours 10minutes") == timedelta(31, 4200)
    assert dtu.parse_time_delta("") == timedelta(0)
    with pytest.raises(ValueError):
        dtu.parse_time_delta("0")


@pytest.mark.parametrize(
    "dttm, timestamp",
    [
        ('2019-01-01 19:30:23.232311', 1546371023.232311),
        ('1981-04-25 02:32:26.456412', 357013946.456412),
        ('1981-04-25 02:32:26', 357013946),
    ]
)
def test_dttm_with_microsecond_to_timestamp(dttm, timestamp):
    assert dtu.timestamp_with_microseconds(dttm) == timestamp


@pytest.mark.parametrize(
    "timestamp, dttm",
    [
        (1546371023.232311, '2019-01-01 19:30:23.232311'),
        (357013946.456412, '1981-04-25 02:32:26.456412'),
        (357013946.0, '1981-04-25 02:32:26.000000'),
    ]
)
def test_timestamp_with_microseconds_to_dttm(timestamp, dttm):
    assert dtu.timestamp2datetime_microseconds(timestamp) == dttm


@pytest.mark.parametrize('window, now, expected', [
    (DateWindow(), '2020-03-13', Period('2020-03-13', '2020-03-13 23:59:59.999999')),
    (DateWindow().start(days=-1), '2020-03-13', Period('2020-03-12', '2020-03-13 23:59:59.999999')),
    (DateWindow().end(seconds=-30), '2020-03-13', Period('2020-03-13', '2020-03-13 23:59:29.999999')),
    (HourWindow(), '2020-03-13 00:00:00', Period('2020-03-13 00:00:00', '2020-03-13 00:59:59.999999')),
    (HourWindow(), '2020-03-13 01:13:22', Period('2020-03-13 01:00:00', '2020-03-13 01:59:59.999999')),
    (HourWindow().start(days=-1), '2020-03-13 01:13:22', Period('2020-03-12 01:00:00', '2020-03-13 01:59:59.999999')),
    (
            HourWindow().start(days=-1, hours=2),
            '2020-03-13 01:13:22',
            Period('2020-03-12 03:00:00', '2020-03-13 01:59:59.999999')
    ),
    (
            HourWindow().start(days=-1, hours=2).end(hours=-1),
            '2020-03-13 01:13:22',
            Period('2020-03-12 03:00:00', '2020-03-13 00:59:59.999999')
    ),
])
def test_window(window, now, expected):
    assert window.apply(dtu.parse_datetime(now)) == expected


@pytest.mark.parametrize('iso_timestring, timezone, expected_dttm', [
    ('2020-03-13 23:59:59.999999', 'UTC', datetime(2020, 3, 13, 23, 59, 59, 999999, pytz.UTC)),
    ('2020-03-13 23:59:59.999999', 'Europe/Moscow', datetime(2020, 3, 13, 20, 59, 59, 999999, pytz.UTC)),
    ('2020-03-13 23:59:59.999999', None, datetime(2020, 3, 13, 23, 59, 59, 999999, pytz.UTC)),
    ('2020-03-13 23:59:59.99999', None, datetime(2020, 3, 13, 23, 59, 59, 999990, pytz.UTC)),
    ('2020-03-13 23:59:59.9999', None, datetime(2020, 3, 13, 23, 59, 59, 999900, pytz.UTC)),
    ('2020-03-13 23:59:59.999', None, datetime(2020, 3, 13, 23, 59, 59, 999000, pytz.UTC)),
    ('2020-03-13 23:59:59.99', None, datetime(2020, 3, 13, 23, 59, 59, 990000, pytz.UTC)),
    ('2020-03-13 23:59:59.9', None, datetime(2020, 3, 13, 23, 59, 59, 900000, pytz.UTC)),
    ('2020-03-13 23:59:59.99999+00:00', 'Europe/Moscow', datetime(2020, 3, 13, 23, 59, 59, 999990, pytz.UTC)),
    ('2020-03-13 23:59:59.9999+00:00', 'Europe/Moscow', datetime(2020, 3, 13, 23, 59, 59, 999900, pytz.UTC)),
    ('2020-03-13 23:59:59.999+00:00', 'Europe/Moscow', datetime(2020, 3, 13, 23, 59, 59, 999000, pytz.UTC)),
    ('2020-03-13 23:59:59.99+00:00', 'Europe/Moscow', datetime(2020, 3, 13, 23, 59, 59, 990000, pytz.UTC)),
    ('2020-03-13 23:59:59.9+00:00', 'Europe/Moscow', datetime(2020, 3, 13, 23, 59, 59, 900000, pytz.UTC)),
    ('2020-03-13 23:59:59+00:00', 'Europe/Moscow', datetime(2020, 3, 13, 23, 59, 59, 0, pytz.UTC)),
    ('2020-03-13 23:59:59.99999+02:00', None, datetime(2020, 3, 13, 21, 59, 59, 999990, pytz.UTC)),
    ('2020-03-13 23:59:59.9999+02:00', None, datetime(2020, 3, 13, 21, 59, 59, 999900, pytz.UTC)),
    ('2020-03-13 23:59:59.999+02:00', None, datetime(2020, 3, 13, 21, 59, 59, 999000, pytz.UTC)),
    ('2020-03-13 23:59:59.99+02:00', None, datetime(2020, 3, 13, 21, 59, 59, 990000, pytz.UTC)),
    ('2020-03-13 23:59:59.9+02:00', None, datetime(2020, 3, 13, 21, 59, 59, 900000, pytz.UTC)),
    ('2020-03-13 23:59:59+02:00', None, datetime(2020, 3, 13, 21, 59, 59, 0, pytz.UTC)),
    ('2020-03-13 23:59:59.999999+0000', None, datetime(2020, 3, 13, 23, 59, 59, 999999, pytz.UTC)),
    ('2020-03-13T23:59:59.999999+0300', None, datetime(2020, 3, 13, 20, 59, 59, 999999, pytz.UTC)),
    ('2020-03-13 23:59:59.999999+0300', None, datetime(2020, 3, 13, 20, 59, 59, 999999, pytz.UTC)),
    ('2020-03-13T23:59:59.999999+03:00', None, datetime(2020, 3, 13, 20, 59, 59, 999999, pytz.UTC)),
    ('2020-03-13 23:59:59.999999+03:00', None, datetime(2020, 3, 13, 20, 59, 59, 999999, pytz.UTC)),
    ('2020-03-13 23:59:59+03', None, datetime(2020, 3, 13, 20, 59, 59, 0, pytz.UTC)),
    ('2020-03-13 23:59:59-02', None, datetime(2020, 3, 14, 1, 59, 59, 0, pytz.UTC)),
    ('2020-03-13 23:59+04', None, datetime(2020, 3, 13, 19, 59, 0, 0, pytz.UTC)),
    ('2020-03-13 23:59:00Z', 'Europe/Moscow', datetime(2020, 3, 13, 23, 59, 0, 0, pytz.UTC)),
])
def test_parse_iso_timestring_to_utc(iso_timestring, timezone, expected_dttm):
    if timezone is None:
        parsed_dttm = dtu.parse_iso_timestring_to_utc(iso_timestring)
    else:
        parsed_dttm = dtu.parse_iso_timestring_to_utc(iso_timestring, timezone)

    assert parsed_dttm == expected_dttm


@pytest.mark.parametrize('iso_timestring, expected_dttm', [
    ('2020-03-13 23:59:59.999999', datetime(2020, 3, 13, 23, 59, 59, 999999)),
    ('2020-03-13 23:59:59.99999', datetime(2020, 3, 13, 23, 59, 59, 999990)),
    ('2020-03-13 23:59:59.9999', datetime(2020, 3, 13, 23, 59, 59, 999900)),
    ('2020-03-13 23:59:59.999', datetime(2020, 3, 13, 23, 59, 59, 999000)),
    ('2020-03-13 23:59:59.99', datetime(2020, 3, 13, 23, 59, 59, 990000)),
    ('2020-03-13 23:59:59.9', datetime(2020, 3, 13, 23, 59, 59, 900000)),
    ('2020-03-13 23:59:59.99999+00:00', datetime(2020, 3, 13, 23, 59, 59, 999990, pytz.UTC)),
    ('2020-03-13 23:59:59.9999+00:00', datetime(2020, 3, 13, 23, 59, 59, 999900, pytz.UTC)),
    ('2020-03-13 23:59:59.999+00:00', datetime(2020, 3, 13, 23, 59, 59, 999000, pytz.UTC)),
    ('2020-03-13 23:59:59.99+00:00', datetime(2020, 3, 13, 23, 59, 59, 990000, pytz.UTC)),
    ('2020-03-13 23:59:59.9+00:00', datetime(2020, 3, 13, 23, 59, 59, 900000, pytz.UTC)),
    ('2020-03-13 23:59:59+00:00', datetime(2020, 3, 13, 23, 59, 59, 0, pytz.UTC)),
    ('2020-03-13 23:59:59Z', datetime(2020, 3, 13, 23, 59, 59, 0, pytz.UTC)),
    ('2020-03-13T23:59:59Z', datetime(2020, 3, 13, 23, 59, 59, 0, pytz.UTC)),
    ('2020-03-13 23:59:59.999999+03:00', datetime(2020, 3, 13, 23, 59, 59, 999999, tz.tzoffset(None, 10800))),
    ('2020-03-13 23:59:59.999+03:00', datetime(2020, 3, 13, 23, 59, 59, 999000, tz.tzoffset(None, 10800))),
    ('2020-03-13 23:59:59+03:00', datetime(2020, 3, 13, 23, 59, 59, 0, tz.tzoffset(None, 10800))),
])
def test_parse_iso_timestring(iso_timestring, expected_dttm):
    parsed_dttm = dtu.parse_iso_timestring(iso_timestring)
    assert parsed_dttm == expected_dttm


@pytest.mark.parametrize('iso_timestring, expected_dttm', [
    ('2021-09-01T12:45:32.547+04:00', '2021-09-01 08:45:32'),
    ('2021-09-01 23:59:59.999999', '2021-09-01 23:59:59'),
    ('2021-09-01 23:59:59.9+00:00', '2021-09-01 23:59:59'),
    ('2021-09-01 23:59:59.999+03:00', '2021-09-01 20:59:59'),
])
def test_iso_timestring_to_utc_datetime(iso_timestring, expected_dttm):
    parsed_dttm = dtu.iso_timestring_to_utc_datetime(iso_timestring)
    assert parsed_dttm == expected_dttm


@pytest.mark.parametrize('iso_timestring, expected_timestamp', [
    ('2021-09-01T12:45:32.547+04:00', 1630485932),
    ('2021-09-01 23:59:59.999999', 1630540799),
    ('2021-09-01 23:59:59.9+00:00', 1630540799),
    ('2021-09-01 23:59:59.999+03:00', 1630529999),
])
def test_iso_timestring_to_timestamp(iso_timestring, expected_timestamp):
    parsed_timestamp = dtu.iso_timestring_to_timestamp(iso_timestring)
    assert parsed_timestamp == expected_timestamp


@pytest.mark.parametrize('date, offset, expected', [
    ('2010-01-01', dict(delta=timedelta(days=10)), '2010-01-11'),
    ('2010-01-01', dict(delta=timedelta(days=10), days=11), '2010-01-11'),
    ('2010-01-01', dict(days=11), '2010-01-12'),
    ('2010-01-01', dict(days=1, hours=10), '2010-01-02 10:00:00'),
])
def test_add_offset(date, offset, expected):
    actual = dtu.add_offset(dtu.parse_datetime(date), **offset)
    assert actual == dtu.parse_datetime(expected)


@pytest.mark.parametrize('delta, microseconds', [
    (timedelta(0, 0, 51622), 51622),
    (timedelta(0, 15, 51622), 15051622),
    (timedelta(3, 15, 51622), 259215051622),
])
def test_total_microseconds(delta, microseconds):
    assert dtu.total_microseconds(delta) == microseconds


@pytest.mark.parametrize('human_timedelta, total_seconds', [
    ('', 0),
    ('31s', 31),
    ('19m', 1140),
    ('19m31s', 1171),
    ('13h', 46800),
    ('13h31s', 46831),
    ('13h19m', 47940),
    ('13h19m31s', 47971),
    ('7d', 604800),
    ('7d31s', 604831),
    ('7d19m', 605940),
    ('7d19m31s', 605971),
    ('7d13h', 651600),
    ('7d13h31s', 651631),
    ('7d13h19m', 652740),
    ('7d13h19m31s', 652771),
    ('0d0h0m0s', 0),
    ('0d0h0m31s', 31),
    ('0d0h19m0s', 1140),
    ('0d0h19m31s', 1171),
    ('0d13h0m0s', 46800),
    ('0d13h0m31s', 46831),
    ('0d13h19m0s', 47940),
    ('0d13h19m31s', 47971),
    ('7d0h0m0s', 604800),
    ('7d0h0m31s', 604831),
    ('7d0h19m0s', 605940),
    ('7d0h19m31s', 605971),
    ('7d13h0m0s', 651600),
    ('7d13h0m31s', 651631),
    ('7d13h19m0s', 652740),
    ('7d13h19m31s', 652771),
])
def test_parse_timedelta_string(human_timedelta, total_seconds):
    assert dtu.parse_timedelta_string(human_timedelta) == total_seconds


@pytest.mark.parametrize(
    'value, expected', [
        (dtu.datetime(2020, 10, 11, 23, 11), dtu.datetime(2020, 10, 11, 20, 11)),
        ('2020-10-11 23:11:00', dtu.datetime(2020, 10, 11, 20, 11)),
    ]
)
def test_msk2utc_wo_tz(value, expected):
    assert expected == dtu.msk2utc_wo_tz(value)


@pytest.mark.parametrize(
    'date,expected',
    [
        ('1970-01-01', 0),
        ('1970-01-01 00:10:15', 0),
        ('1970-01-02', 1),
        ('1970-01-03', 2),
        ('1970-02-01', 31),
    ]
)
def test_unix_date(date, expected):
    date = dtu._to_datetime(date)
    assert dtu.days_unix(date) == expected
    assert dtu.from_days_unix(dtu.days_unix(date)).date() == date.date()


@pytest.mark.parametrize(
    'date,expected',
    [
        ('1970-01-01', 0),
        ('1970-01-01 00:10:15', 10 * 60 + 15),
        ('1970-01-02', 86400),
        ('1970-01-03', 86400 * 2),
        ('1970-02-01', 86400 * 31),
    ]
)
def test_unix_datetime(date, expected):
    date = dtu._to_datetime(date)
    assert dtu.timestamp(date) == expected
    assert dtu.from_timestamp(dtu.timestamp(date)) == date


@pytest.mark.parametrize(
    'date,expected',
    [
        ('1970-01-01', 0),
        ('1970-01-01 00:10:15', (10 * 60 + 15) * 1_000_000),
        ('1970-01-01 00:10:15.000133', (10 * 60 + 15) * 1_000_000 + 133),
        ('1970-01-05 00:10:15.000133', (4 * 86400 + 10 * 60 + 15) * 1_000_000 + 133),
    ]
)
def test_unix_microseconds(date, expected):
    date = dtu._to_datetime(date)
    assert dtu.microseconds_unix(date) == expected
    assert dtu.from_microseconds_unix(dtu.microseconds_unix(date)) == date
