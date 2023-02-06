# pylint: disable=redefined-outer-name,unused-variable,no-method-argument
import datetime
import typing

import pytest

from driver_referrals.generated.cron import run_cron


@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, map_reduce_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_calc_stats_no_task(patch):
    @patch('driver_referrals.jobs.calc_stats.calc_driver_stats')
    def calc_driver_stats(*args, **kwargs):
        assert False

    await run_cron.main(['driver_referrals.jobs.calc_stats', '-t', '0', '-d'])


@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, map_reduce_done, assign_rules_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_calc_stats(cron_context):
    await run_cron.main(['driver_referrals.jobs.calc_stats', '-t', '0', '-d'])

    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            """
            SELECT park_id, driver_id, date,
                   rides_total, rides_accounted, is_frauder
            FROM daily_stats
            ORDER BY park_id, driver_id
            """,
        )

    assert [dict(s) for s in stats] == [
        {
            'park_id': 'p0',
            'driver_id': 'd0',
            'date': datetime.datetime(2019, 4, 20, 0, 0),
            'rides_total': 4,
            'rides_accounted': 1,
            'is_frauder': None,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd1',
            'date': datetime.datetime(2019, 4, 20, 0, 0),
            'rides_total': 2,
            'rides_accounted': 1,
            'is_frauder': None,
        },
    ]


@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, map_reduce_done, assign_rules_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_eats.sql'],
)
@pytest.mark.parametrize(
    ('expected_stats', 'expected_notifications'),
    [
        pytest.param(
            [
                {
                    'park_id': 'p0',
                    'driver_id': 'd0',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 4,
                    'rides_accounted': 1,
                    'is_frauder': None,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd1',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 2,
                    'rides_accounted': 1,
                    'is_frauder': None,
                },
            ],
            [
                {
                    'notification_name': 'daily_stats_updated',
                    'notification_kwargs': {'orders_total': 1},
                    'notification_status': 'created',
                    'referrer_park_id': 'p0',
                    'referrer_driver_id': 'd0',
                    'referral_park_id': 'p1',
                    'referral_driver_id': 'd1',
                    'task_date': datetime.date(2019, 4, 20),
                },
                {
                    'notification_name': 'daily_stats_updated',
                    'notification_kwargs': {'orders_total': 1},
                    'notification_status': 'created',
                    'referrer_park_id': 'p1',
                    'referrer_driver_id': 'd1',
                    'referral_park_id': 'p0',
                    'referral_driver_id': 'd0',
                    'task_date': datetime.date(2019, 4, 20),
                },
            ],
            id='taxi orders',
        ),
        pytest.param(
            [
                {
                    'park_id': 'p0',
                    'driver_id': 'd0',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 4,
                    'rides_accounted': 1,
                    'is_frauder': None,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd1',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 2,
                    'rides_accounted': 1,
                    'is_frauder': None,
                },
            ],
            [
                {
                    'notification_name': 'daily_stats_updated',
                    'notification_kwargs': {'orders_total': 1},
                    'notification_status': 'created',
                    'referrer_park_id': 'p0',
                    'referrer_driver_id': 'd0',
                    'referral_park_id': 'p1',
                    'referral_driver_id': 'd1',
                    'task_date': datetime.date(2019, 4, 20),
                },
                {
                    'notification_name': 'daily_stats_updated',
                    'notification_kwargs': {'orders_total': 1},
                    'notification_status': 'created',
                    'referrer_park_id': 'p1',
                    'referrer_driver_id': 'd1',
                    'referral_park_id': 'p0',
                    'referral_driver_id': 'd0',
                    'task_date': datetime.date(2019, 4, 20),
                },
            ],
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ENABLED_EXTERNAL_ORDER_STATS_OVERWRITE=[
                    'eda',
                ],
            ),
            id='taxi orders (sync disabled, overwrite enabled)',
        ),
        pytest.param(
            [
                {
                    'park_id': 'p0',
                    'driver_id': 'd0',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 4,
                    'rides_accounted': 1,
                    'is_frauder': None,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd1',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 2,
                    'rides_accounted': 1,
                    'is_frauder': None,
                },
            ],
            [
                {
                    'notification_name': 'daily_stats_updated',
                    'notification_kwargs': {'orders_total': 1},
                    'notification_status': 'created',
                    'referrer_park_id': 'p0',
                    'referrer_driver_id': 'd0',
                    'referral_park_id': 'p1',
                    'referral_driver_id': 'd1',
                    'task_date': datetime.date(2019, 4, 20),
                },
                {
                    'notification_name': 'daily_stats_updated',
                    'notification_kwargs': {'orders_total': 1},
                    'notification_status': 'created',
                    'referrer_park_id': 'p1',
                    'referrer_driver_id': 'd1',
                    'referral_park_id': 'p0',
                    'referral_driver_id': 'd0',
                    'task_date': datetime.date(2019, 4, 20),
                },
            ],
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ENABLED_EXTERNAL_ORDER_STATS=['eda'],
            ),
            id='taxi orders (sync enabled, overwrite disabled)',
        ),
        pytest.param(
            [
                {
                    'park_id': 'p0',
                    'driver_id': 'd0',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 4,
                    'rides_accounted': 1,
                    'is_frauder': None,
                },
                {
                    'park_id': 'p1',
                    'driver_id': 'd1',
                    'date': datetime.datetime(2019, 4, 20, 0, 0),
                    'rides_total': 10,
                    'rides_accounted': 10,
                    'is_frauder': None,
                },
            ],
            [
                {
                    'notification_name': 'daily_stats_updated',
                    'notification_kwargs': {'orders_total': 10},
                    'notification_status': 'created',
                    'referrer_park_id': 'p0',
                    'referrer_driver_id': 'd0',
                    'referral_park_id': 'p1',
                    'referral_driver_id': 'd1',
                    'task_date': datetime.date(2019, 4, 20),
                },
                {
                    'notification_name': 'daily_stats_updated',
                    'notification_kwargs': {'orders_total': 1},
                    'notification_status': 'created',
                    'referrer_park_id': 'p1',
                    'referrer_driver_id': 'd1',
                    'referral_park_id': 'p0',
                    'referral_driver_id': 'd0',
                    'task_date': datetime.date(2019, 4, 20),
                },
            ],
            marks=pytest.mark.config(
                DRIVER_REFERRALS_ENABLED_EXTERNAL_ORDER_STATS=['eda'],
                DRIVER_REFERRALS_ENABLED_EXTERNAL_ORDER_STATS_OVERWRITE=[
                    'eda',
                ],
            ),
            id='eda orders',
        ),
    ],
)
async def test_calc_stats_eats(
        cron_context,
        expected_stats: typing.List[typing.Dict[str, typing.Any]],
        expected_notifications: typing.List[typing.Dict[str, typing.Any]],
):
    await run_cron.main(['driver_referrals.jobs.calc_stats', '-t', '0', '-d'])

    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            """
            SELECT park_id, driver_id, date,
                   rides_total, rides_accounted, is_frauder
            FROM daily_stats
            ORDER BY park_id, driver_id
            """,
        )

    assert [dict(s) for s in stats] == expected_stats

    async with cron_context.pg.master_pool.acquire() as conn:
        notifications = await conn.fetch(
            """
            SELECT
                notification_name
                , notification_kwargs
                , notification_status
                , referrer_park_id
                , referrer_driver_id
                , referral_park_id
                , referral_driver_id
                , task_date
            FROM notifications
            ORDER BY referrer_driver_id
            """,
        )
    assert [
        dict(notification) for notification in notifications
    ] == expected_notifications
