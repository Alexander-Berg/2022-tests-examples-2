# -*- coding: utf-8 -*-

from datetime import datetime
import os
from time import (
    mktime,
    time,
    tzset,
)
import unittest

from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.utils.time import (
    daterange,
    datetime_to_integer_unixtime_nullable,
    datetime_to_unixtime,
    parse_datetime,
    parse_unixtime,
    round_timestamp,
    safe_local_datetime_to_date,
    string_to_integer_unixtime,
    unixtime_to_datetime,
    zero_datetime,
)
import pytz


some_day = datetime(2013, 9, 18, 10, 10, 10)
some_time = int(time())


class TestDaterange(unittest.TestCase):
    def setUp(self):
        self.old_tz = os.environ.get('TZ', '')
        # Фиксируем таймзону на MSK, чтобы не ломалось форматирование времени
        os.environ['TZ'] = 'Europe/Moscow'
        tzset()

    def tearDown(self):
        os.environ['TZ'] = self.old_tz
        tzset()

    def test_daterange(self):
        DATE_FORMAT = '%Y-%m-%d'
        d = daterange(
            datetime.strptime('2016-06-30', DATE_FORMAT),
            datetime.strptime('2016-07-03', DATE_FORMAT),
        )
        self.assertEqual(
            list(d),
            [
                datetime.strptime('2016-06-30', DATE_FORMAT),
                datetime.strptime('2016-07-01', DATE_FORMAT),
                datetime.strptime('2016-07-02', DATE_FORMAT),
                datetime.strptime('2016-07-03', DATE_FORMAT),
            ]
        )

    def test_daterange_as_unixtime(self):
        DATE_FORMAT = '%Y-%m-%d'
        d = daterange(
            datetime.strptime('2016-06-30', DATE_FORMAT),
            datetime.strptime('2016-07-03', DATE_FORMAT),
        ).as_unixtime()
        self.assertEqual(
            list(d),
            [1467234000, 1467320400, 1467406800, 1467493200],
        )


class DateTimeWithZeroes(datetime):
    """Специальный класс, который имеет нули на всех временнЫх атрибутах."""

    def __new__(cls, *args, **kwargs):
        return datetime.__new__(cls, 1900, 1, 1)

    def __getattribute__(self, item):
        if item in ['year', 'month', 'day', 'hour', 'minute', 'second']:
            return 0
        return super(DateTimeWithZeroes, self).__getattribute__(item)  # pragma: no cover


class TestTimeUtils(unittest.TestCase):
    def test_datetime_to_unixtime__bad_value__error(self):
        with assert_raises(TypeError):
            invalid_value = 'not-datetime-value'
            datetime_to_unixtime(invalid_value)

    def test_unixtime_to_datetime__good_values__ok(self):
        cases = [
            (1404737593, datetime.fromtimestamp(1404737593)),
            (1404737710.904808, datetime.fromtimestamp(1404737710)),  # отбрасываем доли секунды
            ('1404737785', datetime.fromtimestamp(1404737785))
        ]
        for ts, expected_dt in cases:
            dt = unixtime_to_datetime(ts)
            eq_(dt, expected_dt)

    def test_datetime_to_integer_unixtime_nullable_ok(self):
        cases = [
            (some_day, mktime(some_day.timetuple())),
            (0, None),
            (None, None),
        ]
        for dt, expected_ts in cases:
            ts = datetime_to_integer_unixtime_nullable(dt)
            eq_(ts, expected_ts)

    def test_unixtime_to_datetime__bad_value__error(self):
        with assert_raises(TypeError):
            unixtime_to_datetime('foobar')

    def test_unixtime_to_datetime__another_bad_value__error(self):
        with assert_raises(TypeError):
            unixtime_to_datetime('3.1415')

    def test_parse_datetime_with_undefined_value(self):
        assert_is_none(parse_datetime(None))

    def test_parse_datetime_valid_string_datetime(self):
        eq_(parse_datetime(some_day.strftime('%Y-%m-%d %H:%M:%S')), some_day)

    def test_parse_datetime_with_datetime(self):
        eq_(parse_datetime(some_day), some_day)

    def test_parse_datetime_default_time(self):
        eq_(parse_datetime('0000-00-00 00:00:00'), datetime.fromtimestamp(0))

    def test_safe_local_datetime_to_date(self):
        eq_(
            safe_local_datetime_to_date(
                datetime(2010, 10, 9, 23, 10, 10, 10),
                pytz.timezone('Asia/Vladivostok'),
            ),
            datetime(2010, 10, 10),
        )
        eq_(
            safe_local_datetime_to_date(
                datetime(2010, 10, 9, 11, 10),
                pytz.timezone('Asia/Vladivostok'),
            ),
            datetime(2010, 10, 9),
        )

    def test_parse_unixtime_with_undefined_value(self):
        assert_is_none(parse_unixtime(None))

    def test_parse_datetime_valid_string_unixtime(self):
        eq_(parse_unixtime(str(some_time)), datetime.fromtimestamp(some_time))

    def test_parse_unixtime_default_unixtime_1(self):
        eq_(parse_unixtime('0'), datetime.fromtimestamp(0))

    def test_parse_unixtime_default_unixtime_2(self):
        eq_(parse_unixtime(0), None)

    def test_parse_unixtime_with_unixtime(self):
        eq_(parse_unixtime(some_time), datetime.fromtimestamp(some_time))

    def test_string_to_integer_unixtime(self):
        cases = [
            ('0', 0),
            ('1', 1),
            ('3.14', 3),
            ('1520942379.862289', 1520942379),
            (1520942379.862289, 1520942379),
        ]
        for value, expected_ts in cases:
            eq_(string_to_integer_unixtime(value), expected_ts)

    def test_zero_datetime(self):
        ok_(zero_datetime != datetime(2000, 1, 1, 1, 1, 1))
        ok_(zero_datetime == DateTimeWithZeroes())
        ok_(zero_datetime != 1)
        ok_(zero_datetime == zero_datetime)

    def test_round_timestamp(self):
        TEST_DATETIME = datetime(2012, 1, 2, 3, 4, 5)
        eq_(round_timestamp(TEST_DATETIME.replace(microsecond=10 ** 6 - 1)), TEST_DATETIME)
        eq_(round_timestamp(TEST_DATETIME.replace(microsecond=1)), TEST_DATETIME)
        eq_(round_timestamp(TEST_DATETIME), TEST_DATETIME)
        eq_(round_timestamp(1), 1)
        eq_(round_timestamp(1.0), 1.0)
        eq_(round_timestamp(1.1), 1.0)
        eq_(round_timestamp(1.9), 1.0)

        for unixtime in [-1.9, -1.1, -1.0, -0.9, -0.1, 0.0, 0.1, 0.9, 1.0, 1.1, 1.9]:
            rounded_unixtime = round_timestamp(unixtime)
            rounded_datetime = round_timestamp(datetime.fromtimestamp(unixtime))
            eq_(datetime.fromtimestamp(rounded_unixtime), rounded_datetime)
