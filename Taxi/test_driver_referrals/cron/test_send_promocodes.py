# pylint: disable=redefined-outer-name,unused-variable,global-statement

import pytest

from driver_referrals.generated.cron import run_cron


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """INSERT INTO tasks (id, task_date) """
        """VALUES ('task_id', '2019-04-20')""",
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_send_promocodes_no_task(patch):
    @patch('driver_referrals.common.db.get_drivers_to_send_promocodes')
    def get_drivers_to_send_promocodes(*args, **kwargs):
        assert False

    await run_cron.main(
        ['driver_referrals.jobs.send_promocodes', '-t', '0', '-d'],
    )


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_SERIES_OVERRIDE={'test_series': 'test_series_override'},
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
@pytest.mark.parametrize(
    'is_promocode_created,expected_series',
    ([True, ['test_series_override', 'test_series_2']], [False, None]),
)
async def test_send_promocodes(
        cron_context,
        mockserver,
        patch,
        mock_promocode_response,
        is_promocode_created,
        expected_series,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        return {
            'driver_profiles': [],
            'parks': [{'driver_partner_source': 'yandex'}],
            'total': 1,
            'offset': 0,
        }

    mock_promocode_response.set_response_settings(
        is_promocode_created, expected_series,
    )

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    await run_cron.main(
        ['driver_referrals.jobs.send_promocodes', '-t', '0', '-d'],
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            'SELECT id, status, child_status, current_step '
            'FROM referral_profiles ORDER BY id',
        )
    stats = [dict(r) for r in stats]
    assert stats == [
        {
            'id': 'r1',
            'status': 'completed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r6',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r7',
            'status': 'awaiting_payment',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r8',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r9',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r91',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r92',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r93',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_parent_reward',
            'current_step': 1,
        },
        {
            'id': 'r94',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
    ]


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_SERIES_OVERRIDE={'test_series': 'test_series_override'},
    DRIVER_REFERRALS_PARK_SELFEMPLOYED_CONVERT_SETTING={
        'is_enabled': True,
        'steps': [
            {
                'rides': 1,
                'promocode': {
                    'series': 'test_series',
                    'days_for_activation': 100,
                },
                'child_promocode': {
                    'series': 'test_series',
                    'days_for_activation': 100,
                },
            },
            {
                'rides': 2,
                'promocode': {
                    'series': 'test_series_2',
                    'days_for_activation': 200,
                },
                'child_promocode': {
                    'series': 'test_series_2',
                    'days_for_activation': 200,
                },
            },
        ],
    },
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_park_to_selfemployed.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
@pytest.mark.parametrize(
    'is_promocode_created,expected_series',
    ([True, ['test_series_override', 'test_series_2']], [False, None]),
)
async def test_send_promocodes_park_to_selfemployed(
        cron_context,
        mockserver,
        patch,
        mock_promocode_response,
        is_promocode_created,
        expected_series,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        return {
            'driver_profiles': [],
            'parks': [{'driver_partner_source': 'yandex'}],
            'total': 1,
            'offset': 0,
        }

    mock_promocode_response.set_response_settings(
        is_promocode_created, expected_series,
    )

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def orders_list(request):
        return {
            'orders': [
                {
                    'id': 'order_id_0',
                    'short_id': 123,
                    'status': 'complete',
                    'created_at': '2020-01-01T00:00:00+00:00',
                    'booked_at': '2020-01-01T00:00:00+00:00',
                    'provider': 'platform',
                    'address_from': {
                        'address': (
                            'Street hail: Russia, Moscow,'
                            ' Troparyovsky Forest Park'
                        ),
                        'lat': 55.734803,
                        'lon': 37.643132,
                    },
                    'amenities': [],
                    'events': [],
                    'route_points': [],
                },
            ],
            'limit': 1,
        }

    await run_cron.main(
        ['driver_referrals.jobs.send_promocodes', '-t', '0', '-d'],
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            'SELECT id, status, child_status, current_step '
            'FROM referral_profiles ORDER BY id',
        )
    stats = [dict(r) for r in stats]
    assert stats == [
        {
            'id': 'r1',
            'status': 'completed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r6',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r7',
            'status': 'awaiting_payment',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r8',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r9',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r91',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r92',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r93',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_parent_reward',
            'current_step': 1,
        },
        {
            'id': 'r94',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
    ]


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_SERIES_OVERRIDE={'test_series': 'test_series_override'},
    DRIVER_REFERRALS_PARK_SELFEMPLOYED_CONVERT_SETTING={
        'is_enabled': True,
        'steps': [],
    },
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_park_to_selfemployed.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
@pytest.mark.parametrize(
    'is_promocode_created,expected_series',
    ([True, ['test_series_override', 'test_series_2']], [False, None]),
)
async def test_send_promocodes_park_to_selfemployed_wo_config(
        cron_context,
        mockserver,
        patch,
        mock_promocode_response,
        is_promocode_created,
        expected_series,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        return {
            'driver_profiles': [],
            'parks': [{'driver_partner_source': 'yandex'}],
            'total': 1,
            'offset': 0,
        }

    mock_promocode_response.set_response_settings(
        is_promocode_created, expected_series,
    )

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def orders_list(request):
        return {
            'orders': [
                {
                    'id': 'order_id_0',
                    'short_id': 123,
                    'status': 'complete',
                    'created_at': '2020-01-01T00:00:00+00:00',
                    'booked_at': '2020-01-01T00:00:00+00:00',
                    'provider': 'platform',
                    'address_from': {
                        'address': (
                            'Street hail: Russia, Moscow,'
                            ' Troparyovsky Forest Park'
                        ),
                        'lat': 55.734803,
                        'lon': 37.643132,
                    },
                    'amenities': [],
                    'events': [],
                    'route_points': [],
                },
            ],
            'limit': 1,
        }

    await run_cron.main(
        ['driver_referrals.jobs.send_promocodes', '-t', '0', '-d'],
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            'SELECT id, status, child_status, current_step '
            'FROM referral_profiles ORDER BY id',
        )
    stats = [dict(r) for r in stats]
    assert stats == [
        {
            'id': 'r1',
            'status': 'completed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r6',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r7',
            'status': 'awaiting_payment',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r8',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r9',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r91',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r92',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r93',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_parent_reward',
            'current_step': 1,
        },
        {
            'id': 'r94',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
    ]


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_SERIES_OVERRIDE={'test_series': 'test_series_override'},
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_2.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_send_promocodes_block_self_invite(
        cron_context, mockserver, patch,
):
    @mockserver.json_handler('/driver-promocodes/internal/v1/promocodes')
    async def _(request):
        assert False

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'SAME_LICENSE'

    await run_cron.main(
        ['driver_referrals.jobs.send_promocodes', '-t', '0', '-d'],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        status = await conn.fetchval(
            'SELECT status FROM referral_profiles '
            'WHERE park_id = \'p2\' AND driver_id = \'d2\'',
        )

    assert status == 'blocked'


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_SERIES_OVERRIDE={'test_series': 'test_series_override'},
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, mark_finished_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_2.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_send_promocodes_block_not_new(
        cron_context,
        mockserver,
        patch,
        mock_unique_drivers_retrieve_by_uniques,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        return {
            'driver_profiles': [],
            'parks': [{'driver_partner_source': 'invited_other_park'}],
            'total': 1,
            'offset': 0,
        }

    @mockserver.json_handler('/driver-promocodes/internal/v1/promocodes')
    async def _(request):
        assert False

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    uniques = [
        {
            'park_id': 'p1',
            'driver_profile_id': 'd1',
            'park_driver_profile_id': 'p1_d1',
        },
        {
            'park_id': 'p2',
            'driver_profile_id': 'd2',
            'park_driver_profile_id': 'p2_d2',
        },
        {
            'park_id': 'p3',
            'driver_profile_id': 'd3',
            'park_driver_profile_id': 'p3_d3',
        },
    ]

    mock_unique_drivers_retrieve_by_uniques(
        {'p1_d1': uniques, 'p2_d2': uniques, 'p3_d3': uniques},
    )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    async def orders_list(request):
        return {
            'orders': [
                {
                    'id': 'order_id_0',
                    'short_id': 123,
                    'status': 'complete',
                    'created_at': '2020-01-01T00:00:00+00:00',
                    'booked_at': '2020-01-01T00:00:00+00:00',
                    'provider': 'platform',
                    'address_from': {
                        'address': (
                            'Street hail: Russia, Moscow,'
                            ' Troparyovsky Forest Park'
                        ),
                        'lat': 55.734803,
                        'lon': 37.643132,
                    },
                    'amenities': [],
                    'events': [],
                    'route_points': [],
                },
            ],
            'limit': 1,
        }

    await run_cron.main(
        ['driver_referrals.jobs.send_promocodes', '-t', '0', '-d'],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        status = await conn.fetchval(
            'SELECT status FROM referral_profiles '
            'WHERE park_id = \'p2\' AND driver_id = \'d2\'',
        )

    assert status == 'blocked'
