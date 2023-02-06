# pylint: disable=redefined-outer-name,unused-variable,no-method-argument
import datetime

import pytest

from driver_referrals.common import db as app_db
from driver_referrals.generated.cron import run_cron


@pytest.mark.config(DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """INSERT INTO tasks (id, task_date) """
        """VALUES ('task_id', '2019-04-20')""",
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_mark_finished_no_task(patch):
    @patch('driver_referrals.common.db.get_drivers_in_progress')
    def get_drivers_in_progress(*args, **kwargs):
        assert False

    await run_cron.main(
        ['driver_referrals.jobs.mark_finished', '-t', '0', '-d'],
    )


@pytest.mark.config(DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """
    INSERT INTO tasks (id, task_date, antifraud_check_done)
    VALUES ('task_id', '2019-04-20', '2019-04-20')
    """,
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_mark_finished(cron_context):
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
            'referral_id': 'r2',
            'park_id': 'p2',
            'driver_id': 'd2',
            'started': datetime.datetime(2019, 4, 19, 13, 0),
            'finished': datetime.datetime(2019, 4, 21, 13, 0),
            'rides_accounted': 5,
            'rides_required': 2,
            'referree_days': 2,
            'rule_id': 'r1',
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
            'rides_required': 2,
            'referree_days': 2,
            'rule_id': 'r1',
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
            'rides_required': 2,
            'referree_days': 2,
            'rule_id': 'r1',
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
            'rides_required': 2,
            'referree_days': 2,
            'rule_id': 'r1',
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
            'rides_accounted': 2,
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
            'status': 'in_progress',
            'child_status': None,
            'current_step': 0,
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
            'current_step': 0,
        },
        {
            'id': 'r5',
            'status': 'failed',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r6',
            'status': 'awaiting_payment',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r7',
            'status': 'completed',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r8',
            'status': 'awaiting_promocode',
            'child_status': None,
            'current_step': 0,
        },
        {
            'id': 'r9',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
        {
            'id': 'r91',
            'status': 'in_progress',
            'child_status': 'awaiting_promocode',
            'current_step': 0,
        },
        {
            'id': 'r92',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
    ]


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
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
async def test_mark_finished_park_to_selfemployed(cron_context):
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
            'status': 'awaiting_payment',
            'child_status': 'awaiting_promocode',
            'current_step': 0,
        },
        {
            'id': 'r7',
            'status': 'awaiting_promocode',
            'child_status': 'awaiting_promocode',
            'current_step': 1,
        },
        {
            'id': 'r8',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_promocode',
            'current_step': 0,
        },
        {
            'id': 'r9',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_promocode',
            'current_step': 0,
        },
        {
            'id': 'r91',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_promocode',
            'current_step': 0,
        },
        {
            'id': 'r92',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
    ]


@pytest.mark.config(
    DRIVER_REFERRALS_ENABLE_FINISH_IN_ONE_JOB=False,
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
async def test_mark_finished_park_to_selfemployed_wo_config(cron_context):
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
            'status': 'awaiting_payment',
            'child_status': 'awaiting_promocode',
            'current_step': 0,
        },
        {
            'id': 'r7',
            'status': 'awaiting_promocode',
            'child_status': 'awaiting_promocode',
            'current_step': 1,
        },
        {
            'id': 'r8',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_promocode',
            'current_step': 0,
        },
        {
            'id': 'r9',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_promocode',
            'current_step': 0,
        },
        {
            'id': 'r91',
            'status': 'awaiting_payment',
            'child_status': 'awaiting_promocode',
            'current_step': 0,
        },
        {
            'id': 'r92',
            'status': 'in_progress',
            'child_status': None,
            'current_step': 1,
        },
    ]
