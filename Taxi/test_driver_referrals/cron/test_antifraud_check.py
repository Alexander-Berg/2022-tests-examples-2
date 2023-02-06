# pylint: disable=redefined-outer-name,unused-variable,no-method-argument
import datetime

import pytest

from driver_referrals.common import db as app_db
from driver_referrals.generated.cron import run_cron


@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """INSERT INTO tasks (id, task_date) """
        """VALUES ('task_id', '2019-04-20')""",
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_antifraud_check_no_task(patch):
    @patch('driver_referrals.common.db.get_drivers_to_check_fraud')
    def get_drivers_to_assign_rule(*args, **kwargs):
        assert False

    await run_cron.main(
        ['driver_referrals.jobs.antifraud_check', '-t', '0', '-d'],
    )


@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, calc_stats_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_antifraud_check(patch, cron_context):
    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(_, park_id, driver_id, **kwargs):
        data = {'p1_d1': 'l1', 'p3_d3': 'l3', 'p4_d4': 'l4'}

        return {
            'driver_license': {
                'normalized_number': data[f'{park_id}_{driver_id}'],
            },
        }

    @patch('taxi.clients.antifraud.AntifraudClient._request')
    async def check_referral_fraud(url, data, **kwargs):
        assert data['date'] == '2019-04-21T00:00:00+00:00'
        if data['license'] in ['l1', 'l3']:
            return {'frauder': True}
        if data['license'] == 'l4':
            return {'frauder': False}

        assert False

    drivers_to_check = await app_db.get_drivers_to_check_fraud(
        cron_context, datetime.datetime(2019, 4, 20),
    )

    assert drivers_to_check == [('p1', 'd1'), ('p3', 'd3'), ('p4', 'd4')]

    await run_cron.main(
        ['driver_referrals.jobs.antifraud_check', '-t', '0', '-d'],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            'SELECT id, park_id, driver_id, is_frauder '
            'FROM daily_stats ORDER BY id',
        )
    stats = [dict(r) for r in stats]

    assert stats == [
        {'id': 'ds1', 'park_id': 'p1', 'driver_id': 'd1', 'is_frauder': True},
        {'id': 'ds2', 'park_id': 'p2', 'driver_id': 'd2', 'is_frauder': None},
        {'id': 'ds3', 'park_id': 'p3', 'driver_id': 'd3', 'is_frauder': True},
        {'id': 'ds4', 'park_id': 'p4', 'driver_id': 'd4', 'is_frauder': False},
        {'id': 'ds5', 'park_id': 'p4', 'driver_id': 'd4', 'is_frauder': True},
        {'id': 'ds6', 'park_id': 'p4', 'driver_id': 'd4', 'is_frauder': True},
    ]
