import mock

import pytest

from dmp_suite.datetime_utils import DateWindow, Period, parse_datetime
from dmp_suite.task import cli
from market_b2c_etl.task.cli import StartEndDate


@pytest.mark.parametrize('now_dttm, expected_window', [
    ('2022-04-28 23:33:33', DateWindow().start(days=-2).end(days=0)),
    ('2022-04-28 21:00:00', DateWindow().start(days=-2).end(days=0)),
    ('2022-04-28 20:59:59', DateWindow().start(days=-3).end(days=-1)),
])
def test_msk_timezone_default(now_dttm, expected_window):
    now = parse_datetime(now_dttm)
    with mock.patch('dmp_suite.task.cli.dtu.utcnow', return_value=now):
        args = cli.parse_cli_args(
            {'period': StartEndDate.prev_n_days(3)},
            [],
        )
        expected = expected_window.apply(now)
        assert args.period == expected


def test_msk_timezone_none_default():
    args = cli.parse_cli_args(
        {'period': StartEndDate.prev_n_days(3)},
        ['--start_date', '2022-04-26', '--end_date', '2022-04-28'],
    )
    assert args.period == Period('2022-04-26 00:00:00', '2022-04-28 23:59:59.999999')
