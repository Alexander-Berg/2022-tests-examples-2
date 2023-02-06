# pylint: disable=redefined-outer-name,unused-variable,no-method-argument
# pylint: disable=global-statement,too-many-lines
import datetime
import hashlib

import pytest
import pytz

from taxi.billing.clients.models import billing_orders

from driver_referrals.common import db as app_db
from driver_referrals.common import models
from driver_referrals.generated.cron import run_cron


BILLING_REQUESTS = []  # type: ignore


def prepare_merged_jobs_experiment(client_experiments3):
    args = [
        'd0',
        'd1',
        'd2',
        'd3',
        'd4',
        'd5',
        'd6',
        'd7',
        'd8',
        'd9',
        'd91',
        'd92',
    ]
    for arg in args:
        client_experiments3.add_record(
            consumer='driver-referrals/mark_finished_merged_jobs',
            config_name='driver-referrals_mark_finished_merged_drivers',
            args=[{'name': 'driver_id', 'type': 'string', 'value': arg}],
            value={'use_in_job': True},
        )


@pytest.mark.config(DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=True)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """INSERT INTO tasks (id, task_date) """
        """VALUES ('task_id', '2019-04-20')""",
    ],
    files=['pg_driver_referrals.sql', 'pg_driver_referrals_base.sql'],
)
async def test_mark_finished_no_task(patch):
    @patch('driver_referrals.common.db.get_drivers_in_progress')
    def get_drivers_in_progress(*args, **kwargs):
        assert False

    await run_cron.main(
        ['driver_referrals.jobs.mark_finished', '-t', '0', '-d'],
    )


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=True,
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_ENABLE_WRITE_TO_PAYMENT_MAPPING=True,
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, antifraud_check_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals.sql', 'pg_driver_referrals_base.sql'],
)
@pytest.mark.now('2019-04-17 13:00')
async def test_mark_finished(
        cron_context, patch, mockserver, client_experiments3,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        return {
            'driver_profiles': [],
            'parks': [{'driver_partner_source': 'yandex'}],
            'total': 1,
            'offset': 0,
        }

    prepare_merged_jobs_experiment(client_experiments3)
    drivers_to_finish = await app_db.get_drivers_in_progress(cron_context)

    sorted_drivers = sorted(
        [
            dict(r)
            for r in drivers_to_finish
            if r.get('steps')
            or r['rides_accounted'] >= r['rides_required']
            or r['finished'] < datetime.datetime(2019, 4, 20)
        ],
        key=lambda x: x['referral_id'],
    )
    for driver in sorted_drivers:
        del driver['steps']

    assert sorted_drivers == [
        {
            'referral_id': 'r0',
            'park_id': 'p0',
            'driver_id': 'd0',
            'started': datetime.datetime(2019, 4, 18, 13, 0),
            'finished': datetime.datetime(2019, 4, 20, 13, 0),
            'rides_accounted': 0,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': None,
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r2',
            'park_id': 'p2',
            'driver_id': 'd2',
            'started': datetime.datetime(2019, 4, 19, 13, 0),
            'finished': datetime.datetime(2019, 4, 21, 13, 0),
            'rides_accounted': 5,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': None,
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r3',
            'park_id': 'p3',
            'driver_id': 'd3',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 0,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': None,
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r4',
            'park_id': 'p4',
            'driver_id': 'd4',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': None,
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r5',
            'park_id': 'p5',
            'driver_id': 'd5',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 0,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': None,
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r6',
            'park_id': 'p6',
            'driver_id': 'd6',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 3,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_other_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r7',
            'park_id': 'p7',
            'driver_id': 'd7',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_steps',
            'current_step': 1,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r8',
            'park_id': 'p8',
            'driver_id': 'd8',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r9',
            'park_id': 'p9',
            'driver_id': 'd9',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_same_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r91',
            'park_id': 'p91',
            'driver_id': 'd91',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_same_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r92',
            'park_id': 'p92',
            'driver_id': 'd92',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 0,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_same_park',
            'status': 'awaiting_child_reward',
            'child_status': 'awaiting_parent_reward',
        },
    ]

    @mockserver.json_handler('/driver-promocodes/internal/v1/promocodes')
    async def _(request):
        assert (
            request.json['can_activate_until'] == '2019-06-01T16:00:00+03:00'
        )
        return mockserver.make_response(status=200, json={'id': 'promocode1'})

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        return billing_orders.ProcessDocResponse(doc_id=10)

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    await run_cron.main(
        ['driver_referrals.jobs.mark_finished', '-t', '0', '-d'],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        stats = await conn.fetch(
            'SELECT id, status, child_status, current_step '
            'FROM referral_profiles ORDER BY id',
        )

    stats = [dict(r) for r in stats]
    assert stats == [
        {
            'id': 'r0',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r1',
            'status': 'completed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r2',
            'status': 'completed',
            'child_status': None,
            'current_step': 2,
        },
        {
            'id': 'r3',
            'status': 'failed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r4',
            'status': 'failed',
            'child_status': None,
            'current_step': 2,
        },
        {
            'id': 'r5',
            'status': 'failed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r6',
            'status': 'completed',
            'child_status': None,
            'current_step': 2,
        },
        {
            'id': 'r7',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 2,
        },
        {
            'id': 'r8',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 2,
        },
        {
            'id': 'r9',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r91',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r92',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
    ]


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=True,
    DRIVER_REFERRALS_SEND_PROMOCODES={
        'is_enabled': True,
        'series': ['test_series', 'test_series_2'],
    },
    DRIVER_REFERRALS_ENABLE_WRITE_TO_PAYMENT_MAPPING=True,
    DRIVER_REFERRALS_PARK_SELFEMPLOYED_CONVERT_SETTING={
        'is_enabled': True,
        'steps': [
            {
                'rides': 1,
                'payment': 100,
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
    INSERT INTO tasks (id, task_date, antifraud_check_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_park_to_selfemployed.sql'],
)
async def test_mark_finished_merged_park_to_selfemployed(
        cron_context,
        mockserver,
        patch,
        client_experiments3,
        mock_promocode_response,
):
    mock_promocode_response.set_response_settings(
        True, ['test_series', 'test_series_2'],
    )
    prepare_merged_jobs_experiment(client_experiments3)

    drivers_to_finish = await app_db.get_drivers_in_progress(cron_context)

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        return {
            'driver_profiles': [],
            'parks': [{'driver_partner_source': 'yandex'}],
            'total': 1,
            'offset': 0,
        }

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        return billing_orders.ProcessDocResponse(doc_id=10)

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    sorted_drivers = sorted(
        [
            dict(r)
            for r in drivers_to_finish
            if r.get('steps')
            or r['rides_accounted'] >= r['rides_required']
            or r['finished'] < datetime.datetime(2019, 4, 20)
        ],
        key=lambda x: x['referral_id'],
    )
    for driver in sorted_drivers:
        del driver['steps']

    assert sorted_drivers == [
        {
            'referral_id': 'r6',
            'park_id': 'p6',
            'driver_id': 'd6',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r7',
            'park_id': 'p7',
            'driver_id': 'd7',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 1,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r8',
            'park_id': 'p8',
            'driver_id': 'd8',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r9',
            'park_id': 'p9',
            'driver_id': 'd9',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r91',
            'park_id': 'p91',
            'driver_id': 'd91',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r92',
            'park_id': 'p92',
            'driver_id': 'd92',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 0,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'awaiting_child_reward',
            'child_status': 'awaiting_parent_reward',
        },
    ]

    await run_cron.main(
        ['driver_referrals.jobs.mark_finished', '-t', '0', '-d'],
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
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r7',
            'status': 'completed',
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
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r91',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r92',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
    ]


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=True,
    DRIVER_REFERRALS_SEND_PROMOCODES={
        'is_enabled': True,
        'series': ['test_series', 'test_series_2'],
    },
    DRIVER_REFERRALS_ENABLE_WRITE_TO_PAYMENT_MAPPING=True,
    DRIVER_REFERRALS_PARK_SELFEMPLOYED_CONVERT_SETTING={
        'is_enabled': True,
        'steps': [],
    },
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, antifraud_check_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_park_to_selfemployed.sql'],
)
async def test_mark_finished_merged_park_to_selfemployed_wo_config(
        cron_context,
        mockserver,
        patch,
        client_experiments3,
        mock_promocode_response,
):
    mock_promocode_response.set_response_settings(
        True, ['test_series', 'test_series_2'],
    )
    prepare_merged_jobs_experiment(client_experiments3)

    drivers_to_finish = await app_db.get_drivers_in_progress(cron_context)

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        return {
            'driver_profiles': [],
            'parks': [{'driver_partner_source': 'yandex'}],
            'total': 1,
            'offset': 0,
        }

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        return billing_orders.ProcessDocResponse(doc_id=10)

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    sorted_drivers = sorted(
        [
            dict(r)
            for r in drivers_to_finish
            if r.get('steps')
            or r['rides_accounted'] >= r['rides_required']
            or r['finished'] < datetime.datetime(2019, 4, 20)
        ],
        key=lambda x: x['referral_id'],
    )
    for driver in sorted_drivers:
        del driver['steps']

    assert sorted_drivers == [
        {
            'referral_id': 'r6',
            'park_id': 'p6',
            'driver_id': 'd6',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r7',
            'park_id': 'p7',
            'driver_id': 'd7',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 1,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r8',
            'park_id': 'p8',
            'driver_id': 'd8',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r9',
            'park_id': 'p9',
            'driver_id': 'd9',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r91',
            'park_id': 'p91',
            'driver_id': 'd91',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 2,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'in_progress',
            'child_status': None,
        },
        {
            'referral_id': 'r92',
            'park_id': 'p92',
            'driver_id': 'd92',
            'started': datetime.datetime(2019, 4, 17, 13, 0),
            'finished': datetime.datetime(2019, 4, 19, 13, 0),
            'rides_accounted': 0,
            'rides_required': None,
            'referree_days': 2,
            'rule_id': 'rule_with_child_steps',
            'current_step': 0,
            'invite_promocode': 'ПРОМОКОД1',
            'reward_reason': 'invited_selfemployed_from_park',
            'status': 'awaiting_child_reward',
            'child_status': 'awaiting_parent_reward',
        },
    ]

    await run_cron.main(
        ['driver_referrals.jobs.mark_finished', '-t', '0', '-d'],
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
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r7',
            'status': 'completed',
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
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r91',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r92',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
    ]


@pytest.mark.config(
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_SERIES_OVERRIDE={'test_series': 'test_series_override'},
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=True,
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, antifraud_check_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=[
        'pg_driver_referrals_promocode.sql',
        'pg_driver_referrals_base.sql',
    ],
)
@pytest.mark.parametrize(
    'is_promocode_created,expected_series',
    ([True, ['test_series', 'test_series_override']], [False, None]),
)
async def test_promocodes_send(
        patch,
        mockserver,
        client_experiments3,
        is_promocode_created,
        expected_series,
):
    prepare_merged_jobs_experiment(client_experiments3)

    @mockserver.json_handler('/driver-promocodes/internal/v1/promocodes')
    async def _(request):
        series_name = request.json['series_name']
        if expected_series:
            assert series_name in expected_series
        return mockserver.make_response(
            status=(200 if is_promocode_created else 400),
            json={'id': 'promocode1'},
        )

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        return billing_orders.ProcessDocResponse(doc_id=10)

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    await run_cron.main(
        ['driver_referrals.jobs.mark_finished', '-t', '0', '-d'],
    )


@pytest.mark.config(
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=True,
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, antifraud_check_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_payments.sql', 'pg_driver_referrals_base.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_create_payments(patch, mockserver, client_experiments3):
    prepare_merged_jobs_experiment(client_experiments3)

    global BILLING_REQUESTS
    BILLING_REQUESTS = []

    @mockserver.json_handler('/driver-promocodes/internal/v1/promocodes')
    async def _(request):
        return mockserver.make_response(status=200, json={'id': 'promocode1'})

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        global BILLING_REQUESTS
        BILLING_REQUESTS += [request]
        return billing_orders.ProcessDocResponse(doc_id=10)

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'{park_id}_dl'

    await run_cron.main(
        ['driver_referrals.jobs.mark_finished', '-t', '0', '-d'],
    )

    def sort_key(x):
        return x.external_obj_id

    assert sorted(BILLING_REQUESTS, key=sort_key) == sorted(
        [
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r2/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r2/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.utc,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r2/0/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r2/2/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r2/2/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.utc,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r2/2/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r4/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r4/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.utc,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r4/0/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r6/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r6/0/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.utc,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r6/0/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
            billing_orders.ProcessDocRequest(
                kind='driver_referral_payment',
                external_obj_id='driver_referrals/'
                + hashlib.md5(
                    ('r6/2/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                external_event_ref='driver_referrals/'
                + hashlib.md5(
                    ('r6/2/' + str(models.Role.REFERRER)).encode(),
                ).hexdigest(),
                event_at=datetime.datetime(
                    2019, 4, 20, 13, 1, tzinfo=pytz.utc,
                ),
                data={
                    'amount': '100',
                    'currency': 'RUB',
                    'db_id': 'p1',
                    'driver_license': 'p1_dl',
                    'due': '2019-04-20T13:01:00.000000+00:00',
                    'invite_id': hashlib.md5(
                        ('r6/2/' + str(models.Role.REFERRER)).encode(),
                    ).hexdigest(),
                    'invited_driver': 'A B C',
                    'park_id': 'p1_clid',
                    'uuid': 'd1',
                },
                service='driver-referrals',
                reason='',
            ),
        ],
        key=sort_key,
    )


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=True,
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_SERIES_OVERRIDE={'test_series': 'test_series_override'},
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, antifraud_check_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_2.sql', 'pg_driver_referrals_base.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_mark_finished_block_self_invite(
        cron_context, mockserver, patch, client_experiments3,
):
    prepare_merged_jobs_experiment(client_experiments3)

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        assert False

    @mockserver.json_handler('/driver-promocodes/internal/v1/promocodes')
    async def _(request):
        assert False

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

    @patch('driver_referrals.common.parks.get_clid_and_driver_license')
    async def get_clid_and_driver_license(_, park_id, *args, **kwargs):
        return f'{park_id}_clid', f'SAME_LICENSE'

    await run_cron.main(
        ['driver_referrals.jobs.mark_finished', '-t', '0', '-d'],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        statuses = await conn.fetch(
            """
            SELECT status FROM referral_profiles
            WHERE park_id = 'p2' AND driver_id = 'd2'
            OR park_id = 'p4' AND driver_id = 'd4'
            OR park_id = 'p5' AND driver_id = 'd5'
            OR park_id = 'p6' AND driver_id = 'd6'
            OR park_id = 'p7' AND driver_id = 'd7'
            ORDER BY status
            """,
        )

    assert ['blocked', 'blocked', 'blocked', 'in_progress', 'in_progress'] == [
        status['status'] for status in statuses
    ]


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=True,
    DRIVER_REFERRALS_SEND_PROMOCODES={'is_enabled': True, 'series': []},
    DRIVER_REFERRALS_SERIES_OVERRIDE={'test_series': 'test_series_override'},
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, antifraud_check_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals_2.sql', 'pg_driver_referrals_base.sql'],
)
@pytest.mark.now('2019-04-20 13:01')
async def test_mark_finished_send_promocodes_block_not_new(
        cron_context,
        mockserver,
        patch,
        client_experiments3,
        mock_unique_drivers_retrieve_by_uniques,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _(request):
        return {
            'driver_profiles': [],
            'parks': [{'driver_partner_source': 'selfemployed_fns'}],
            'total': 1,
            'offset': 0,
        }

    prepare_merged_jobs_experiment(client_experiments3)

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
        {
            'park_id': 'p4',
            'driver_profile_id': 'd4',
            'park_driver_profile_id': 'p4_d4',
        },
        {
            'park_id': 'p5',
            'driver_profile_id': 'd5',
            'park_driver_profile_id': 'p5_d5',
        },
    ]

    mock_unique_drivers_retrieve_by_uniques(
        {
            'p1_d1': uniques,
            'p2_d2': uniques,
            'p3_d3': uniques,
            'p4_d4': uniques,
            'p5_d5': uniques,
        },
    )

    @patch(
        'taxi.billing.clients.billing_orders.BillingOrdersApiClient'
        '.process_event',
    )
    async def process_events(request, *args, **kwargs):
        assert False

    @patch('driver_referrals.common.parks.get_driver_info')
    async def get_driver_info(*args, **kwargs):
        return {'last_name': 'A', 'first_name': 'B', 'middle_name': 'C'}

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
        ['driver_referrals.jobs.mark_finished', '-t', '0', '-d'],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        statuses = await conn.fetch(
            """
            SELECT status FROM referral_profiles
            WHERE park_id = 'p2' AND driver_id = 'd2'
            OR park_id = 'p4' AND driver_id = 'd4'
            OR park_id = 'p5' AND driver_id = 'd5'
            ORDER BY status
            """,
        )

    assert ['blocked', 'blocked', 'in_progress'] == [
        status['status'] for status in statuses
    ]
