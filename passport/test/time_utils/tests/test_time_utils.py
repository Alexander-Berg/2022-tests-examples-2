# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import (
    datetime,
    timedelta,
)
import time

from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)


def test_datetimenow_eq():
    assert DatetimeNow() == datetime.now()
    assert DatetimeNow(convert_to_datetime=True) == datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    assert not DatetimeNow() == 111
    assert DatetimeNow() != datetime.now() + timedelta(hours=24)
    assert DatetimeNow(convert_to_datetime=True) != '-'


def test_datetimenow_repr():
    assert repr(DatetimeNow())


def test_datetimenow_add():
    day = timedelta(hours=24)
    assert DatetimeNow() + day == datetime.now() + day


def test_datetimenow_deepcopy():
    time = DatetimeNow()
    other = deepcopy(time)

    attrs = {
        'year',
        'month',
        'day',
        'minute',
        'second',
        'microsecond',
        'tzinfo',
        '_delta',
        '_format',
        '_convert_to_datetime',
    }
    for attr in attrs:
        assert getattr(time, attr) == getattr(other, attr)
    assert other is not time


def test_timenow_eq():
    assert TimeNow() == time.time()
    assert TimeNow() == str(time.time())
    assert TimeNow() == TimeNow()
    assert not TimeNow() == 'abc'
    # да, проверяю равенство, а не is None
    assert not TimeNow() == None  # noqa


def test_timenow_repr():
    assert repr(TimeNow())


def test_time_now_milliseconds():
    assert repr(TimeNow(as_milliseconds=True))
