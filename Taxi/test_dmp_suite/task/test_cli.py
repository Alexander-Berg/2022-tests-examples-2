import mock
import pytest
import argparse

from typing import List

from connection.yt import Pool
from dmp_suite import scales
from dmp_suite.datetime_utils import Period, Window, parse_datetime, DateWindow
from dmp_suite.scales import month
from dmp_suite.task import cli
from datetime import datetime


class TestYtPool:
    def test_yt_pool(self):
        pool = Pool.TAXI_DWH_PRIORITY
        args = cli.parse_cli_args({'pool': cli.YTPool()}, ['--pool', pool.value])
        assert args.pool == pool

    def test_default_yt_pool(self):
        pool = Pool.TAXI_DWH_BATCH
        args = cli.parse_cli_args({'pool': cli.YTPool(pool)}, [])
        assert args.pool == pool

    def test_invalid_yt_pool(self):
        with pytest.raises(SystemExit):
            cli.parse_cli_args({'pools': cli.YTPool()}, ['--pool', 'value'])


class TestStartEndDate:
    def test_args(self):
        try:
            args = cli.parse_cli_args(
                {'period': cli.StartEndDate(None)},
                ['--start_date', '2020-01-01', '--end_date', '2020-01-10'])
        except Exception as exc:
            import traceback
            traceback.print_exc()
            raise
        assert args.period == Period('2020-01-01', '2020-01-10 23:59:59.999999')

    def test_args_with_datetime(self):
        args = cli.parse_cli_args(
            {'period': cli.StartEndDate(None, datetime_type='datetime')},
            ['--start_date', '2020-01-01T02:12:34', '--end_date', '2020-01-02T03:00:00']
        )
        assert args.period == Period('2020-01-01 02:12:34', '2020-01-02 03:00:00')

    def test_no_args_no_default(self):
        args = cli.parse_cli_args(
            {'period': cli.StartEndDate(None)},
            [])
        assert args.period is None

    def test_default(self):
        default_period = Period('2020-01-01', '2020-01-10')
        args = cli.parse_cli_args(
            {'period': cli.StartEndDate(default_period)},
            [])
        assert args.period == Period('2020-01-01', '2020-01-10 23:59:59.999999')

    def test_error_if_only_start_or_end(self):
        # Если указано только начало или конец диапазона,
        # то это следует считать ошибкой.
        # Прежде мы возвращали default, и это выглядело странно

        task_args = {'period': cli.StartEndDate.yesterday()}
        cli_args = ['--start_date', '2020-01-01']

        with pytest.raises(argparse.ArgumentTypeError):
            cli.parse_cli_args(task_args, cli_args)

        cli_args = ['--end_date', '2020-01-01']

        with pytest.raises(argparse.ArgumentTypeError):
            cli.parse_cli_args(task_args, cli_args)

    @pytest.mark.parametrize('scale, expected', [
        (scales.day, Period('2011-10-27 00:00:00', '2011-10-27 23:59:59.999999')),
        (scales.week, Period('2011-10-17 00:00:00', '2011-10-23 23:59:59.999999')),
        (scales.month, Period('2011-09-01 00:00:00', '2011-09-30 23:59:59.999999')),
        (scales.year, Period('2010-01-01 00:00:00', '2010-12-31 23:59:59.999999')),
    ])
    def test_prev_calendar_period(self, scale, expected):
        now = parse_datetime('2011-10-28 23:23:23')
        with mock.patch('dmp_suite.task.cli.dtu.utcnow', return_value=now):
            args = cli.parse_cli_args(
                {'period': cli.StartEndDate.prev_calendar_period(scale)},
                [],
            )
            assert args.period == expected

    def test_prev_n_days(self):
        now = parse_datetime('2000-01-03 23:23:23')
        with mock.patch('dmp_suite.task.cli.dtu.utcnow', return_value=now):
            args = cli.parse_cli_args(
                {'period': cli.StartEndDate.prev_n_days(2)},
                [],
            )
            expected_window = DateWindow().start(days=-2).end(days=-1)
            expected = expected_window.apply(now)
            assert args.period == expected

    @pytest.mark.parametrize('n, scale, skip_current, expected', [
        (1, scales.day, False, Period('2011-10-28 00:00:00', '2011-10-28 23:59:59.999999')),
        (2, scales.day, False, Period('2011-10-27 00:00:00', '2011-10-28 23:59:59.999999')),
        (1, scales.day, True, Period('2011-10-27 00:00:00', '2011-10-27 23:59:59.999999')),
        (2, scales.day, True, Period('2011-10-26 00:00:00', '2011-10-27 23:59:59.999999')),

        (1, scales.week, False, Period('2011-10-24 00:00:00', '2011-10-30 23:59:59.999999')),
        (2, scales.week, False, Period('2011-10-17 00:00:00', '2011-10-30 23:59:59.999999')),
        (1, scales.week, True, Period('2011-10-17 00:00:00', '2011-10-23 23:59:59.999999')),
        (2, scales.week, True, Period('2011-10-10 00:00:00', '2011-10-23 23:59:59.999999')),

        (1, scales.month, False, Period('2011-10-01 00:00:00', '2011-10-31 23:59:59.999999')),
        (2, scales.month, False, Period('2011-09-01 00:00:00', '2011-10-31 23:59:59.999999')),
        (1, scales.month, True, Period('2011-09-01 00:00:00', '2011-09-30 23:59:59.999999')),
        (2, scales.month, True, Period('2011-08-01 00:00:00', '2011-09-30 23:59:59.999999')),

        (1, scales.year, False, Period('2011-01-01 00:00:00', '2011-12-31 23:59:59.999999')),
        (2, scales.year, False, Period('2010-01-01 00:00:00', '2011-12-31 23:59:59.999999')),
        (1, scales.year, True, Period('2010-01-01 00:00:00', '2010-12-31 23:59:59.999999')),
        (2, scales.year, True, Period('2009-01-01 00:00:00', '2010-12-31 23:59:59.999999')),
    ])
    def test_last_n_calendar_period(self, n, scale, skip_current, expected):
        now = parse_datetime('2011-10-28 23:23:23')
        with mock.patch('dmp_suite.task.cli.dtu.utcnow', return_value=now):
            start_end_date_args = cli.StartEndDate.last_n_calendar_period(
                n, scale, skip_current
            )
            args = cli.parse_cli_args(
                {'period': start_end_date_args},
                [],
            )
            assert args.period == expected

    @pytest.mark.parametrize('n, scale, now_str, expected', [
        (
            1, scales.day,
            '2011-10-28 23:23:23',
            Period('2011-10-27 00:00:00', '2011-10-27 23:59:59.999999')
        ),
        (
            2, scales.day,
            '2011-10-28 23:23:23',
            Period('2011-10-26 00:00:00', '2011-10-27 23:59:59.999999')
        ),
        # проверяем на границе годов
        (
            1, scales.day,
            '2011-01-01 11:11:11',
            Period('2010-12-31 00:00:00', '2010-12-31 23:59:59.999999')
        ),
        (
            2, scales.day,
            '2011-01-01 11:11:11',
            Period('2010-12-30 00:00:00', '2010-12-31 23:59:59.999999')
        ),

        (
            1, scales.week,
            '2011-10-28 23:23:23',
            Period('2011-10-24 00:00:00', '2011-10-27 23:59:59.999999')
        ),
        (
            2, scales.week,
            '2011-10-28 23:23:23',
            Period('2011-10-17 00:00:00', '2011-10-27 23:59:59.999999')
        ),
        # на границе недель
        (
            1, scales.week,
            '2011-10-31 11:11:11',
            Period('2011-10-24 00:00:00', '2011-10-30 23:59:59.999999')
        ),
        (
            2, scales.week,
            '2011-10-31 11:11:11',
            Period('2011-10-17 00:00:00', '2011-10-30 23:59:59.999999')
        ),

        (
            1, scales.month,
            '2011-10-28 23:23:23',
            Period('2011-10-01 00:00:00', '2011-10-27 23:59:59.999999')
        ),
        (
            2, scales.month,
            '2011-10-28 23:23:23',
            Period('2011-09-01 00:00:00', '2011-10-27 23:59:59.999999')
        ),

        (
            1, scales.year,
            '2011-10-28 23:23:23',
            Period('2011-01-01 00:00:00', '2011-10-27 23:59:59.999999')
        ),
        (
            2, scales.year,
            '2011-10-28 23:23:23',
            Period('2010-01-01 00:00:00', '2011-10-27 23:59:59.999999')
        ),
    ])
    def test_last_n_calendar_period_till_yesterday(self, n, scale, now_str, expected):
        now = parse_datetime(now_str)
        with mock.patch('dmp_suite.task.cli.dtu.utcnow', return_value=now):
            start_end_date_args = cli.StartEndDate.last_n_calendar_period_till_yesterday(
                n, scale
            )
            args = cli.parse_cli_args(
                {'period': start_end_date_args},
                [],
            )
            assert args.period == expected


class TestStartEndDatetime:
    _NOW = parse_datetime('2000-01-03 23:23:23')

    def test_datetime_args(self):
        args = cli.parse_cli_args(
            {'period': cli.StartEndDatetime(None)},
            ['--start_date', '2020-01-01T02:12:34', '--end_date', '2020-01-02T03:00:00']
        )
        assert args.period == Period('2020-01-01 02:12:34', '2020-01-02 03:00:00')

    def test_date_only_args(self):
        args = cli.parse_cli_args(
            {'period': cli.StartEndDatetime(None)},
            ['--start_date', '2020-01-01', '--end_date', '2020-01-10']
        )
        assert args.period == Period('2020-01-01 00:00:00', '2020-01-10 00:00:00')


class TestPeriod:
    def test_period(self):
        args = cli.parse_cli_args(
            {'period': cli.Period(None)},
            ['--period', '2020-01-01', '2020-01-10'])
        assert args.period == Period('2020-01-01', '2020-01-10')

    def test_no_args_no_default(self):
        args = cli.parse_cli_args(
            {'period': cli.Period(None)},
            [])
        assert args.period is None

    def test_default_period(self):
        default_period = Period('2020-01-01', '2020-01-10')
        args = cli.parse_cli_args(
            {'period': cli.Period(default_period)},
            [])
        assert args.period == default_period

    def test_default_callback(self):
        default_period = Period('2020-01-01', '2020-01-10')

        def callback() -> Period:
            return default_period

        args = cli.parse_cli_args(
            {'period': cli.Period(callback)},
            [])
        assert args.period == default_period

    def test_default_window(self):
        window = Window().replace(minute=0, second=0, microsecond=0)
        args = cli.parse_cli_args(
            {'period': cli.Period(window)},
            [])
        assert args.period == window.apply()


class TestDisjointedPeriods:
    def test_disjointed_periods(self):
        dttm_format = '%Y-%m-%dT%H:%M:%S:%f'
        args = cli.parse_cli_args(
            {'partition_dates': cli.DisjointedPeriods(None)},
            ['--partition_dates', '2020-01-01', '2020-01-03', '2020-04-10'])
        assert args.partition_dates == [
            Period('2020-01-01', datetime.strptime('2020-01-01T23:59:59:999999',dttm_format)),
            Period('2020-01-03', datetime.strptime('2020-01-03T23:59:59:999999',dttm_format)),
            Period('2020-04-10', datetime.strptime('2020-04-10T23:59:59:999999',dttm_format))]

    def test_disjointed_periods_with_extension(self):
        dttm_format = '%Y-%m-%dT%H:%M:%S:%f'
        args = cli.parse_cli_args(
            {'partition_dates': cli.DisjointedPeriods(None, scale=month)},
            ['--partition_dates', '2020-01-01', '2020-01-03', '2020-04-10'])
        assert args.partition_dates == [
            Period('2020-01-01', datetime.strptime('2020-01-31T23:59:59:999999',dttm_format)),
            Period('2020-01-01', datetime.strptime('2020-01-31T23:59:59:999999',dttm_format)),
            Period('2020-04-01', datetime.strptime('2020-04-30T23:59:59:999999',dttm_format))]

    def test_no_args_no_default(self):
        args = cli.parse_cli_args(
            {'partition_dates': cli.DisjointedPeriods(None)},
            [])
        assert args.partition_dates is None

    def test_default_period(self):
        default_periods = [Period('2020-01-01', '2020-01-10'),Period('2020-10-01', '2020-10-15')]
        args = cli.parse_cli_args(
            {'partition_dates': cli.DisjointedPeriods(default_periods)},
            [])
        assert args.partition_dates == default_periods



@pytest.mark.parametrize('args, raw_args, expected', [
    (
        {'start_date': cli.Datetime(None)},
        [],
        None,
    ),
    (
        {'start_date': cli.Datetime(None)},
        ['--start_date', '2020-01-01'],
        parse_datetime('2020-01-01'),
    ),
    (
        {'start_date': cli.Datetime('2020-01-01')},
        [],
        parse_datetime('2020-01-01'),
    ),
    (
        {'start_date': cli.Datetime(parse_datetime('2020-01-01'))},
        [],
        parse_datetime('2020-01-01'),
    ),
    (
        {'start_date': cli.Datetime(lambda: parse_datetime('2020-01-01'))},
        [],
        parse_datetime('2020-01-01'),
    ),
    (
        {'start_date': cli.Datetime.round_up(
            scale=scales.day,
            base=lambda: parse_datetime('2020-01-01 10:01:01'),
        )},
        [],
        scales.day.extract_end(parse_datetime('2020-01-01 10:01:01')),
    ),
    (
        {'start_date': cli.Datetime.round_down(
            scale=scales.day,
            base=lambda: parse_datetime('2020-01-01 10:01:01'),
        )},
        [],
        scales.day.extract_start(parse_datetime('2020-01-01 10:01:01')),
    ),
])
def test_datetime(args, raw_args, expected):
    args = cli.parse_cli_args(args, raw_args)
    assert args.start_date == expected


def test_datetime_yesterday():
    now = parse_datetime('2020-01-02 10:01:01')
    with mock.patch('dmp_suite.task.cli.dtu.utcnow', return_value=now):
        arg = cli.Datetime.yesterday()
        args = {'start_date': arg}
        expected = parse_datetime('2020-01-01')
        assert cli.parse_cli_args(args, []).start_date == expected


def test_bool_arg():
    args = dict(overwrite=cli.Flag())

    result = cli.parse_cli_args(args, [])
    assert result.overwrite is False

    result = cli.parse_cli_args(args, ['--overwrite'])
    assert result.overwrite is True


