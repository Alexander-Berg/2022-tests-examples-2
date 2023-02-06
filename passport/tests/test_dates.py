# -*- coding: utf-8 -*-
from datetime import (
    date,
    datetime,
    timedelta,
)
import time
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.compare.compare import FACTOR_NOT_SET
import passport.backend.core.compare.dates as dates
from passport.backend.core.compare.dates import (
    _build_approximation,
    _build_linear_parameters,
    _date_difference_error,
    BIRTHDAYS_FACTOR_FULL_MATCH,
    BIRTHDAYS_FACTOR_INEXACT_MATCH,
    BIRTHDAYS_FACTOR_NO_MATCH,
    calculate_timestamp_depth_factor,
    calculate_timestamp_interval_factor,
    compare_birthdays_inexact,
    compare_dates_loose,
    LOOSE_DATE_THRESHOLD_FACTOR,
)
from passport.backend.core.types.birthday import Birthday
import pytz


TEST_REFERENCE_POINTS = [
    (1, 1),
    (2, 1),  # k = 0.0, b = 1.0
    (4, 1.5),  # k = 0.5 / 2, b = 1 - 0.25 * 2 = 0.5
    (8, 3),  # k = 1.5 / 4, b = 1.5 - 1.5 / 4 * 4 = 0.0
]
TEST_REFERENCE_ERROR = 0.2
TEST_LOOSE_DATE_THRESHOLD = 1.0 - TEST_REFERENCE_ERROR

TEST_REFERENCE_POINTS_FOR_EVENT_DEPTH = [
    (0, 1),
    (1, 1),
    (3, 3),
    (6, 3),
    (30, 30),
    (90, 30),
    (120, 60),
    (360, 60),
]


class TestCompareDatesLoose(unittest.TestCase):
    def setUp(self):
        self.patches = [
            mock.patch('passport.backend.core.compare.dates._RECALLED_BY_USER_REFERENCE_POINTS', TEST_REFERENCE_POINTS),
            mock.patch('passport.backend.core.compare.dates._REFERENCE_ERROR', TEST_REFERENCE_ERROR),
            mock.patch('passport.backend.core.compare.dates.LOOSE_DATE_THRESHOLD_FACTOR', TEST_LOOSE_DATE_THRESHOLD),
        ]

        for patch in self.patches:
            patch.start()

        self.approximation_patch = mock.patch(
            'passport.backend.core.compare.dates.RECALLED_BY_USER_ALLOWED_DELTA_FUNC',
            _build_approximation(_build_linear_parameters(TEST_REFERENCE_POINTS)),
        )
        self.approximation_patch.start()

        self.approximation = dates.RECALLED_BY_USER_ALLOWED_DELTA_FUNC

    def tearDown(self):
        self.approximation_patch.stop()
        for patch in reversed(self.patches):
            patch.stop()

    def test_approximation(self):
        test_points = [
            (0, 1),
            (1.5, 1),
            (3, 1.25),
            (6, 2.25),
            (16, 6),
        ]
        for x, y in TEST_REFERENCE_POINTS + test_points:
            eq_(self.approximation(x), y)

    def test_date_difference_error_reference(self):
        test_points = [
            (0, 1),
            (1.5, 1),
            (3, 1.25),
            (6, 2.25),
            (16, 6),
        ]
        for x, y in TEST_REFERENCE_POINTS + test_points:
            eq_(
                _date_difference_error(x, y),
                TEST_REFERENCE_ERROR,
            )

    def test_date_difference_error(self):
        test_points_errors = [
            (0, 2, 1.0),
            (8, 7, 0.2 + 0.8 * 4 / 5),  # 0.84
            (8, 5, 0.2 + 0.8 * 2 / 5),  # 0.52
            (8, 1.5, 0.1),
            (8, 0.75, 0.05),
            (8, 0, 0.0),
            (16, 7, 0.2 + 0.8 * 0.1),  # 0.28
            (16, 100, 1.0),
            (80, 20, 0.2 * 20 / 30),  # 0.1(3)
            (80, 31, 0.2 + 0.8 * 1 / 50),  # 0.216
        ]
        for x, y, error in test_points_errors:
            eq_(
                _date_difference_error(x, y),
                error,
            )

    def test_compare_dates_loose(self):
        now = datetime.now()
        today_date = date.today()
        today_date_as_datetime = datetime(today_date.year, today_date.month, today_date.day)
        test_dates_factors = [
            (now, now, 1.0),
            (datetime.now(), now, 1.0),
            (datetime.now(), datetime.now(), 1.0),
            (datetime.now(), today_date_as_datetime, 1.0),
            (today_date_as_datetime, datetime.now(), 1.0),
            (today_date_as_datetime + timedelta(days=30), now, 0.0),  # оригинальная дата в будущем
            (now + timedelta(minutes=5), now, 0.0),  # оригинальная дата в будущем
            (now, datetime.now() + timedelta(days=1), 0.0),  # введенная дата в будущем
            (now + timedelta(days=-1), now, 0.8),
            (now + timedelta(days=-1), now + timedelta(days=-2), 0.8),
            (now + timedelta(days=-1), now + timedelta(days=-3), 0.0),
            (now + timedelta(days=-8), now + timedelta(days=-3), 0.48),
            (now + timedelta(days=-80), now + timedelta(days=-60), 1 - 0.2 * 20 / 30),
        ]
        for i, (orig_date, supplied_date, factor) in enumerate(test_dates_factors):
            eq_(
                compare_dates_loose(orig_date, supplied_date),
                factor,
            )

    def test_compare_dates_loose_in_different_tz(self):
        original_date = datetime(2014, 12, 24)
        supplied_date = datetime(2014, 12, 25)
        # Настоящий момент подобран так, чтобы в часовом поясе Екатеринбурга
        # (+2 часа) с момента ввода прошло 5 суток, а в часовом поясе Москвы 4
        # суток. Т.к. к точности даты предъялвяются более мягкие требования, если
        # она старше 5 суток.
        now = datetime(2014, 12, 29, 22, 5, 0)
        with mock.patch(u'passport.backend.core.compare.dates.datetime') as datetime_mock:
            datetime_mock.now.return_value = now

            factor = compare_dates_loose(
                original_date,
                supplied_date,
                pytz.timezone(u'Asia/Yekaterinburg'),
            )
            eq_(factor, 41. / 45)

            factor = compare_dates_loose(
                original_date,
                supplied_date,
                pytz.timezone(u'Europe/Moscow'),
            )
            eq_(factor, 67. / 75)


class TestCompareDatesLooseActualData(unittest.TestCase):

    def test_approximation_slopes_valid(self):
        parameters = _build_linear_parameters(dates._RECALLED_BY_USER_REFERENCE_POINTS)
        ok_(len(parameters) > 0)
        prev_k = None
        for date_oldness, k, b in parameters:
            ok_(0.0 <= k <= 1.0)
            if prev_k is not None:
                ok_(prev_k <= k)
            prev_k = k

    def test_approximation_points(self):
        test_points = dates._RECALLED_BY_USER_REFERENCE_POINTS
        approximation = dates.RECALLED_BY_USER_ALLOWED_DELTA_FUNC
        for x, y in test_points:
            eq_(approximation(x), y)


FLOAT_EPS = 1e-6


class TestCalculateDepthFactor(unittest.TestCase):
    def test_approximation_points(self):
        test_points = dates._EVENT_DEPTH_REFERENCE_POINTS
        approximation = dates.EVENT_DEPTH_THRESHOLD_FUNC
        for x, y in test_points:
            eq_(approximation(x), y)

    def test_calculate_factor(self):
        now_ts = time.time()
        reg_ts_1 = now_ts - timedelta(days=2).total_seconds()
        reg_ts_2 = now_ts - timedelta(days=1000).total_seconds()
        reg_ts_3 = now_ts - timedelta(days=60).total_seconds()
        reg_ts_4 = now_ts - timedelta(hours=15).total_seconds()
        with mock.patch(
            'passport.backend.core.compare.dates.EVENT_DEPTH_THRESHOLD_FUNC',
            _build_approximation(_build_linear_parameters(TEST_REFERENCE_POINTS_FOR_EVENT_DEPTH)),
        ):
            timestamps_factors = (
                (reg_ts_1, now_ts, 0.0),  # совпадает с временем сейчас
                (reg_ts_1, reg_ts_1, LOOSE_DATE_THRESHOLD_FACTOR),  # порог равен глубине регистрации
                (reg_ts_1, reg_ts_1 - 1, FACTOR_NOT_SET),  # глубже чем timestamp регистрации - некорректная ситуация
                (reg_ts_1, reg_ts_1 + timedelta(days=3).total_seconds(), FACTOR_NOT_SET),  # время в будущем
                (reg_ts_2, now_ts - timedelta(days=375).total_seconds(), 1.0),  # глубже чем год назад
                (reg_ts_3, now_ts - timedelta(days=15).total_seconds(), LOOSE_DATE_THRESHOLD_FACTOR / 2),
                (reg_ts_3, now_ts - timedelta(days=45).total_seconds(), (LOOSE_DATE_THRESHOLD_FACTOR + 1) / 2),
                (reg_ts_4, now_ts - timedelta(hours=12).total_seconds(), LOOSE_DATE_THRESHOLD_FACTOR / 2),  # регистрация меньше дня назад - порог равен одному дню
            )
            for i, (reg_ts, event_ts, expected_factor) in enumerate(timestamps_factors):
                factor = calculate_timestamp_depth_factor(reg_ts, now_ts, event_ts)
                ok_(abs(factor - expected_factor) < FLOAT_EPS, '%d: found %s, expected %s' % (i, factor, expected_factor))

    def test_calculate_factor_with_fixed_threshold(self):
        now_ts = time.time()
        reg_ts_1 = now_ts - timedelta(days=10).total_seconds()
        reg_ts_2 = now_ts - timedelta(days=1000).total_seconds()
        reg_ts_3 = now_ts - timedelta(days=2, hours=12).total_seconds()
        timestamps_factors = (
            (reg_ts_1, now_ts, 0.0),  # совпадает с временем сейчас
            (reg_ts_1, reg_ts_1, 1.0),  # совпадает с timestamp регистрации
            (reg_ts_1, reg_ts_1 - 1, FACTOR_NOT_SET),  # глубже чем timestamp регистрации
            (reg_ts_1, now_ts - timedelta(days=5).total_seconds(), LOOSE_DATE_THRESHOLD_FACTOR),  # на границе фиксированного порога
            (reg_ts_1, reg_ts_1 + timedelta(days=7, hours=12).total_seconds(), LOOSE_DATE_THRESHOLD_FACTOR / 2),
            (reg_ts_2, now_ts - timedelta(days=375).total_seconds(), 1.0),  # глубже чем год назад
            (reg_ts_3, reg_ts_3, LOOSE_DATE_THRESHOLD_FACTOR / 2),  # порог глубже чем регистрация
        )
        for i, (reg_ts, event_ts, expected_factor) in enumerate(timestamps_factors):
            factor = calculate_timestamp_depth_factor(reg_ts, now_ts, event_ts, fixed_threshold=timedelta(days=5).total_seconds())
            ok_(abs(factor - expected_factor) < FLOAT_EPS, '%d: found %s, expected %s' % (i, factor, expected_factor))


class TestCalculateIntervalFactor(unittest.TestCase):
    def test_valid_values(self):
        now_ts = time.time()
        reg_ts_1 = now_ts - timedelta(days=10).total_seconds()
        reg_ts_2 = now_ts - timedelta(days=1000).total_seconds()
        timestamps_factors = (
            (reg_ts_1, now_ts, now_ts, 0.0),  # интервал длиной 0
            (reg_ts_1, reg_ts_1, now_ts, 1.0),  # интервал длиной от момента регистрации до текущего момента
            (reg_ts_1, reg_ts_1 + timedelta(days=5).total_seconds(), now_ts, 0.5),  # половина глубины регистрации
            (reg_ts_2, reg_ts_2, now_ts, 1.0),  # обрезаем по глубине в год
            (reg_ts_2, reg_ts_2, reg_ts_2 + timedelta(days=400).total_seconds(), 1.0),  # обрезаем по глубине в год
        )
        for i, (reg_ts, first_ts, last_ts, expected_factor) in enumerate(timestamps_factors):
            factor = calculate_timestamp_interval_factor(reg_ts, now_ts, first_ts, last_ts)
            ok_(abs(factor - expected_factor) < FLOAT_EPS, '%d: found %s, expected %s' % (i, factor, expected_factor))


def test_compare_birthdays_inexact():
    values_factors = [
        (Birthday(2010, 10, 11), Birthday(2010, 10, 11), BIRTHDAYS_FACTOR_FULL_MATCH),
        (Birthday(2010, 10, 11), Birthday(1010, 10, 11), BIRTHDAYS_FACTOR_INEXACT_MATCH),
        (Birthday(2010, 11, 11), Birthday(2010, 10, 11), BIRTHDAYS_FACTOR_NO_MATCH),
        (Birthday(2010, 10, 11), Birthday(2010, 10, 10), BIRTHDAYS_FACTOR_NO_MATCH),
        # Високосные случаи
        (Birthday(1988, 2, 29), Birthday(1989, 2, 28), BIRTHDAYS_FACTOR_NO_MATCH),
        (Birthday(1989, 2, 28), Birthday(1988, 2, 29), BIRTHDAYS_FACTOR_NO_MATCH),
        (Birthday(1988, 2, 29), Birthday(1992, 2, 29), BIRTHDAYS_FACTOR_INEXACT_MATCH),
        (None, Birthday(2010, 10, 10), FACTOR_NOT_SET),
        (Birthday(2010, 10, 10), '', FACTOR_NOT_SET),
    ]
    for orig_birthday, supplied_birthday, factor in values_factors:
        eq_(compare_birthdays_inexact(orig_birthday, supplied_birthday), factor)
