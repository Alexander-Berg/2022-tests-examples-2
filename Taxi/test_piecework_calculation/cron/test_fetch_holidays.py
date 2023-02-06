# pylint: disable=redefined-outer-name
import datetime

import pytest

from piecework_calculation import calculation_rules
from piecework_calculation import oebs

OEBS_HOLIDAYS = {
    'logins': [
        {
            'login': 'some_login',
            'holiday': [
                datetime.date(2020, 1, 1).isoformat(),
                datetime.date(2020, 1, 7).isoformat(),
                datetime.date(2020, 1, 13).isoformat(),
            ],
        },
        {
            'login': 'other_login',
            'holiday': [
                datetime.date(2020, 1, 1).isoformat(),
                datetime.date(2020, 1, 2).isoformat(),
                datetime.date(2020, 1, 7).isoformat(),
            ],
        },
    ],
}


@pytest.fixture
def mock_oebs_empty_holidays(mockserver):
    @mockserver.json_handler('/oebs/rest/holiday')
    def _holiday(request):
        return {
            'logins': [
                {'login': 'some_login', 'holiday': []},
                {'login': 'other_login', 'holiday': []},
            ],
        }

    return _holiday


async def test_fetch(cron_context, mock_oebs_holidays):
    mocked_holidays = mock_oebs_holidays(OEBS_HOLIDAYS)
    async with cron_context.pg.slave_pool.acquire() as conn:
        rule = await calculation_rules.find_by_id(
            cron_context, 'periodic_rule_id', conn,
        )
        holidays = await oebs.fetch_holidays(
            context=cron_context,
            conn=conn,
            rule=rule,
            logins=['some_login', 'other_login'],
        )
    assert holidays == {
        'some_login': [
            datetime.date(2020, 1, 1),
            datetime.date(2020, 1, 7),
            datetime.date(2020, 1, 13),
        ],
        'other_login': [
            datetime.date(2020, 1, 1),
            datetime.date(2020, 1, 2),
            datetime.date(2020, 1, 7),
        ],
    }
    async with cron_context.pg.slave_pool.acquire() as conn:
        oebs_pg_result = await conn.fetch(
            'SELECT login, holiday_date FROM piecework.oebs_holiday '
            'ORDER by login, holiday_date',
        )
        oebs_pg_result = [dict(item) for item in oebs_pg_result]
        assert oebs_pg_result == [
            {
                'login': 'other_login',
                'holiday_date': datetime.date(2020, 1, 1),
            },
            {
                'login': 'other_login',
                'holiday_date': datetime.date(2020, 1, 2),
            },
            {
                'login': 'other_login',
                'holiday_date': datetime.date(2020, 1, 7),
            },
            {'login': 'some_login', 'holiday_date': datetime.date(2020, 1, 1)},
            {'login': 'some_login', 'holiday_date': datetime.date(2020, 1, 7)},
            {
                'login': 'some_login',
                'holiday_date': datetime.date(2020, 1, 13),
            },
        ]

    holiday_call = mocked_holidays.next_call()
    assert holiday_call['request'].json == {
        'login': ['some_login', 'other_login'],
        'date_from': '2020-01-01',
        'date_to': '2020-01-15',
    }


async def test_fetch_empty(cron_context, mock_oebs_empty_holidays):
    async with cron_context.pg.slave_pool.acquire() as conn:
        rule = await calculation_rules.find_by_id(
            cron_context, 'periodic_rule_id', conn,
        )
        await oebs.fetch_holidays(
            context=cron_context,
            conn=conn,
            rule=rule,
            logins=['some_login', 'other_login'],
        )
    async with cron_context.pg.slave_pool.acquire() as conn:
        holidays_count = await conn.fetchval(
            'SELECT COUNT(*) FROM piecework.oebs_holiday',
        )
        assert not holidays_count
