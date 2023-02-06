# pylint: disable=W0212
import datetime
import typing

import pytest

from taxi_qc_exams.crontasks import setup_exam_deadlines


def _date(month: int, day: int) -> datetime.date:
    return datetime.date(1900, month, day)


def _date_windows1() -> typing.List[dict]:
    return [
        dict(date_begin=_date(7, 1), date_end=_date(12, 31), ranges='w1'),
        dict(date_begin=_date(12, 31), date_end=_date(6, 30), ranges='w2'),
    ]


def _date_windows2() -> typing.List[dict]:
    return [
        dict(date_begin=_date(10, 1), date_end=_date(4, 30), ranges='w1'),
        dict(date_begin=_date(6, 1), date_end=_date(9, 30), ranges='w2'),
    ]


@pytest.mark.parametrize(
    'windows, deadline, result',
    [
        (_date_windows1(), datetime.datetime(1994, 11, 30), 'w1'),
        (_date_windows1(), datetime.datetime(2018, 4, 15), 'w2'),
        (_date_windows1(), datetime.datetime(2009, 12, 31), 'w1'),
        (_date_windows1(), datetime.datetime(2018, 1, 1), 'w2'),
        (_date_windows2(), datetime.datetime(2018, 11, 30), 'w1'),
        (_date_windows2(), datetime.datetime(2013, 4, 15), 'w1'),
        (_date_windows2(), datetime.datetime(2018, 12, 31), 'w1'),
        (_date_windows2(), datetime.datetime(1987, 1, 1), 'w1'),
        (_date_windows2(), datetime.datetime(2023, 5, 23), None),
    ],
)
def test_find_window_by_date(windows, deadline, result):
    date_windows = setup_exam_deadlines._find_windows_by_date(
        windows, deadline.date(),
    )
    assert date_windows == result


def _time(hour: int, minutes: int) -> datetime.time:
    return datetime.time(hour, minutes)


def _time_windows1() -> typing.List[dict]:
    return [
        dict(time_begin=_time(8, 0), time_end=_time(12, 0)),
        dict(time_begin=_time(16, 30), time_end=_time(20, 30)),
    ]


def _time_windows2() -> typing.List[dict]:
    return [
        dict(time_begin=_time(20, 0), time_end=_time(2, 0)),
        dict(time_begin=_time(6, 15), time_end=_time(12, 15)),
        dict(time_begin=_time(16, 30), time_end=_time(18, 30)),
    ]


@pytest.mark.parametrize(
    'windows, deadline, time_begin, time_end',
    [
        (_time_windows1(), datetime.time(5, 0), _time(8, 0), _time(12, 0)),
        (_time_windows1(), datetime.time(9, 8), None, None),
        (
            _time_windows1(),
            datetime.time(14, 18),
            _time(16, 30),
            _time(20, 30),
        ),
        (_time_windows1(), datetime.time(20, 0), None, None),
        (_time_windows1(), datetime.time(0, 0), _time(8, 0), _time(12, 0)),
        (_time_windows2(), datetime.time(0, 0), None, None),
        (_time_windows2(), datetime.time(5, 3), _time(6, 15), _time(12, 15)),
        (_time_windows2(), datetime.time(19, 3), _time(20, 0), _time(2, 0)),
    ],
)
def test_find_next_time_window(windows, deadline, time_begin, time_end):
    begin, end = setup_exam_deadlines._find_next_time_window(windows, deadline)

    assert begin == time_begin
    assert end == time_end
