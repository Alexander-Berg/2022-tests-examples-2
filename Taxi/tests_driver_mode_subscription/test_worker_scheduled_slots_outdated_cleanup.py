import datetime as dt
from typing import Any
from typing import Dict
from typing import List
import uuid

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import scheduled_slots_tools

_SLOT_ID_1 = uuid.UUID('a936b353-fcda-4b7a-b569-a7fb855819dd')
_OFFER_IDENTITY_1 = {'slot_id': str(_SLOT_ID_1), 'rule_version': 1}

_SLOT_ID_2 = uuid.UUID('b7ae5704-cbce-4f67-9a72-c128bad3e63f')
_OFFER_IDENTITY_2 = {'slot_id': str(_SLOT_ID_2), 'rule_version': 1}

_SLOT_ID_3 = uuid.UUID('9fc36842-1d90-4b68-b066-c05cd618f3df')
_OFFER_IDENTITY_3 = {'slot_id': str(_SLOT_ID_3), 'rule_version': 1}

_SLOT_ID_4 = uuid.UUID('0d96469a-bf98-4482-8dba-7c8f71860332')
_OFFER_IDENTITY_4 = {'slot_id': str(_SLOT_ID_4), 'rule_version': 1}


_DRIVER_PROFILE_1 = driver.Profile('parkid1_uuid1')
_DRIVER_PROFILE_2 = driver.Profile('parkid2_uuid2')
_DRIVER_PROFILE_3 = driver.Profile('parkid3_uuid3')
_DRIVER_PROFILE_4 = driver.Profile('parkid4_uuid4')


@pytest.mark.parametrize(
    'enabled_tasks',
    (
        pytest.param(['cleanup_scheduled_slots_reservations']),
        pytest.param(['cleanup_scheduled_slots_meta']),
        pytest.param(['cleanup_scheduled_slots']),
        pytest.param(['cleanup_cancel_reservations']),
        pytest.param(['cleanup_scheduled_slots_quotas']),
        pytest.param(['cleanup_scheduled_slots_abandoned_meta']),
        pytest.param(
            [
                'cleanup_scheduled_slots_reservations',
                'cleanup_scheduled_slots_meta',
                'cleanup_scheduled_slots',
                'cleanup_cancel_reservations',
                'cleanup_scheduled_slots_quotas',
                'cleanup_scheduled_slots_abandoned_meta',
            ],
        ),
    ),
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_outdated_cleanup_enable_tasks(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        taxi_config,
        enabled_tasks: List[str],
):
    worker_config: Dict[str, Any] = {
        'work_interval_ms': 0,
        'operations': {'__default__': {'enabled': False}},
    }

    for task in enabled_tasks:
        worker_config['operations'][task] = {'enabled': True}

    taxi_config.set_values(
        {
            'DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_OUTDATED_CLEANUP': (
                worker_config
            ),
        },
    )

    @testpoint('scheduled-slots-outdated-cleanup-worker-testpoint')
    def worker_testpoint(data):
        pass

    @testpoint('scheduled-slots-outdated-cleanup-task-testpoint')
    def task_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-outdated-cleanup',
    )

    await worker_testpoint.wait_call()

    assert task_testpoint.times_called == len(enabled_tasks)

    called_tasks = []
    while task_testpoint.has_calls:
        called_tasks.append(task_testpoint.next_call()['data']['name'])

    assert set(called_tasks) == set(enabled_tasks)


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_OUTDATED_CLEANUP={
        'work_interval_ms': 0,
        'operations': {
            '__default__': {'enabled': False},
            'cleanup_scheduled_slots_reservations': {
                'enabled': True,
                'delay_s': 3600,
            },
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            'some_mode',
            _OFFER_IDENTITY_1,
            dt.datetime(2021, 5, 5, 10, 3, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 5, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_2.hex,
            'some_mode',
            _OFFER_IDENTITY_2,
            dt.datetime(2021, 5, 6, 10, 3, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 6, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_3.hex,
            'some_mode',
            _OFFER_IDENTITY_3,
            dt.datetime(2021, 5, 7, 10, 3, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 7, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_1.hex,
            _DRIVER_PROFILE_1,
            True,
            dt.datetime(2020, 4, 4, 3, 30, tzinfo=dt.timezone.utc),
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_2.hex,
            _DRIVER_PROFILE_1,
            True,
            dt.datetime(2020, 4, 4, 4, 30, tzinfo=dt.timezone.utc),
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode',
            _SLOT_ID_3.hex,
            _DRIVER_PROFILE_1,
            False,
            dt.datetime(2020, 4, 4, 3, 30, tzinfo=dt.timezone.utc),
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_outdated_cleanup_slot_reservations(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
):
    @testpoint('scheduled-slots-outdated-cleanup-worker-testpoint')
    def worker_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-outdated-cleanup',
    )

    await worker_testpoint.wait_call()

    reservations = scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _DRIVER_PROFILE_1,
    )

    deleted_reservations = scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _DRIVER_PROFILE_1, True,
    )

    reservations_slot_id = set((record[0] for record in reservations))
    deleted_reservations_slot_id = set(
        (record[0] for record in deleted_reservations),
    )

    assert reservations_slot_id == set((_SLOT_ID_3.hex,))
    assert deleted_reservations_slot_id == set((_SLOT_ID_2.hex,))


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_OUTDATED_CLEANUP={
        'work_interval_ms': 0,
        'operations': {
            '__default__': {'enabled': False},
            'cleanup_scheduled_slots_meta': {
                'enabled': True,
                'delay_s': 3600,
                'chunk_size': 1,
            },
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_slot_meta_query(
            _SLOT_ID_1.hex,
            dt.datetime(2020, 4, 4, 4, 30, tzinfo=dt.timezone.utc),
        ),
        scheduled_slots_tools.make_insert_slot_meta_query(
            _SLOT_ID_2.hex,
            dt.datetime(2020, 4, 4, 3, 30, tzinfo=dt.timezone.utc),
        ),
        scheduled_slots_tools.make_insert_slot_meta_query(
            _SLOT_ID_3.hex,
            dt.datetime(2020, 4, 4, 3, 30, tzinfo=dt.timezone.utc),
        ),
        scheduled_slots_tools.make_insert_slot_meta_query(_SLOT_ID_4.hex),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_outdated_cleanup_meta(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
):
    @testpoint('scheduled-slots-outdated-cleanup-worker-testpoint')
    def worker_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-outdated-cleanup',
    )

    await worker_testpoint.wait_call()

    assert (
        len(
            scheduled_slots_tools.get_scheduled_slots_meta(
                pgsql, _SLOT_ID_1.hex,
            ),
        )
        == 1
    )

    assert (
        len(
            scheduled_slots_tools.get_scheduled_slots_meta(
                pgsql, _SLOT_ID_2.hex,
            ),
        )
        + len(
            scheduled_slots_tools.get_scheduled_slots_meta(
                pgsql, _SLOT_ID_3.hex,
            ),
        )
        == 1
    )

    assert (
        len(
            scheduled_slots_tools.get_scheduled_slots_meta(
                pgsql, _SLOT_ID_4.hex,
            ),
        )
        == 1
    )


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_OUTDATED_CLEANUP={
        'work_interval_ms': 0,
        'operations': {
            '__default__': {'enabled': False},
            'cleanup_scheduled_slots': {
                'enabled': True,
                'delay_s': 3600,
                'chunk_size': 1,
            },
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        # No reservations, not in outdated_time - should stay
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            'some_mode',
            _OFFER_IDENTITY_1,
            dt.datetime(2020, 4, 4, 2, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 4, 30, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        # No reservations, in outdated_time - should be deleted
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_2.hex,
            'some_mode',
            _OFFER_IDENTITY_2,
            dt.datetime(2020, 4, 4, 2, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 3, 30, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        # No reservations, in outdated_time - should be deleted
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_3.hex,
            'some_mode',
            _OFFER_IDENTITY_3,
            dt.datetime(2020, 4, 4, 2, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 3, 30, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        # With reservations, in outdated_time - should stay
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_4.hex,
            'some_mode',
            _OFFER_IDENTITY_4,
            dt.datetime(2020, 4, 4, 2, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 3, 30, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_4.hex, _DRIVER_PROFILE_1, True,
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_outdated_cleanup_scheduled_slots(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
):
    @testpoint('scheduled-slots-outdated-cleanup-worker-testpoint')
    def worker_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-outdated-cleanup',
    )

    await worker_testpoint.wait_call()

    slots = scheduled_slots_tools.get_scheduled_slots(pgsql)
    slots_ids = set((record[0] for record in slots))

    expected_to_stay = set((_SLOT_ID_1.hex, _SLOT_ID_4.hex))
    expected_to_be_deleted = set((_SLOT_ID_2.hex, _SLOT_ID_3.hex))

    # check that only chunk_size (== 1) slots were deleted
    was_not_deleted = slots_ids.intersection(expected_to_be_deleted)
    assert len(was_not_deleted) == 1

    slots_ids = slots_ids.difference(was_not_deleted)

    assert slots_ids == expected_to_stay


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_OUTDATED_CLEANUP={
        'work_interval_ms': 0,
        'operations': {
            '__default__': {'enabled': False},
            'cleanup_cancel_reservations': {
                'enabled': True,
                'delay_s': 3600,
                'chunk_size': 1,
            },
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        # not in outdated_time - should stay
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            'some_mode',
            _OFFER_IDENTITY_1,
            dt.datetime(2020, 4, 4, 2, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 4, 30, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        # outdated_time - for cancelling
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_2.hex,
            'some_mode',
            _OFFER_IDENTITY_2,
            dt.datetime(2020, 4, 4, 2, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 3, 30, tzinfo=dt.timezone.utc),
            'some_quota2',
            10,
        ),
        # not in outdated_time - should stay
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_1.hex, _DRIVER_PROFILE_1, False,
        ),
        # outdated_time - should be deleted
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_2.hex, _DRIVER_PROFILE_2, False,
        ),
        # outdated_time - should be deleted
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_2.hex, _DRIVER_PROFILE_3, False,
        ),
        # outdated_time, but already deleted
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_2.hex, _DRIVER_PROFILE_4, True,
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_outdated_cancel_reservations(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
):
    @testpoint('scheduled-slots-outdated-cleanup-worker-testpoint')
    def worker_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-outdated-cleanup',
    )

    await worker_testpoint.wait_call()

    driver1_reservations = scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _DRIVER_PROFILE_1,
    )
    driver1_deleted_reservations = (
        scheduled_slots_tools.get_reservations_by_profile(
            pgsql, _DRIVER_PROFILE_1, True,
        )
    )
    driver2_reservations = scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _DRIVER_PROFILE_2,
    )
    driver2_deleted_reservations = (
        scheduled_slots_tools.get_reservations_by_profile(
            pgsql, _DRIVER_PROFILE_2, True,
        )
    )
    driver3_reservations = scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _DRIVER_PROFILE_3,
    )
    driver3_deleted_reservations = (
        scheduled_slots_tools.get_reservations_by_profile(
            pgsql, _DRIVER_PROFILE_3, True,
        )
    )
    driver4_reservations = scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _DRIVER_PROFILE_4,
    )
    driver4_deleted_reservations = (
        scheduled_slots_tools.get_reservations_by_profile(
            pgsql, _DRIVER_PROFILE_4, True,
        )
    )

    assert len(driver1_reservations) == 1
    assert not driver1_deleted_reservations

    assert len(driver2_reservations) + len(driver3_reservations) == 1
    assert (
        len(driver2_deleted_reservations) + len(driver3_deleted_reservations)
        == 1
    )

    assert not driver4_reservations
    assert len(driver4_deleted_reservations) == 1

    assert scheduled_slots_tools.get_scheduled_quota(pgsql, 'some_quota1') == [
        ('some_quota1', 10),
    ]

    assert scheduled_slots_tools.get_scheduled_quota(pgsql, 'some_quota2') == [
        ('some_quota2', 9),
    ]


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_OUTDATED_CLEANUP={
        'work_interval_ms': 0,
        'operations': {
            '__default__': {'enabled': False},
            'cleanup_scheduled_slots_quotas': {
                'enabled': True,
                'delay_s': 3600,
                'chunk_size': 1,
            },
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        # created recently - should stay
        scheduled_slots_tools.make_update_slot_quota_query(
            'some_quota1',
            0,
            dt.datetime(2020, 4, 4, 4, 30, tzinfo=dt.timezone.utc),
        ),
        # created long time ago, no slots - delete
        scheduled_slots_tools.make_update_slot_quota_query(
            'some_quota2',
            0,
            dt.datetime(2020, 4, 4, 3, 0, tzinfo=dt.timezone.utc),
        ),
        # created long time ago, no slots - delete
        scheduled_slots_tools.make_update_slot_quota_query(
            'some_quota3',
            0,
            dt.datetime(2020, 4, 4, 3, 0, tzinfo=dt.timezone.utc),
        ),
        # created long time ago, have slot - should stay
        scheduled_slots_tools.make_update_slot_quota_query(
            'some_quota4',
            0,
            dt.datetime(2020, 4, 4, 3, 0, tzinfo=dt.timezone.utc),
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            'some_mode',
            _OFFER_IDENTITY_1,
            dt.datetime(2020, 4, 4, 2, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 8, 30, tzinfo=dt.timezone.utc),
            'some_quota4',
            10,
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_outdated_cleanup_quotas(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
):
    @testpoint('scheduled-slots-outdated-cleanup-worker-testpoint')
    def worker_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-outdated-cleanup',
    )

    await worker_testpoint.wait_call()

    quota1_records = scheduled_slots_tools.get_scheduled_quota(
        pgsql, 'some_quota1',
    )
    quota2_records = scheduled_slots_tools.get_scheduled_quota(
        pgsql, 'some_quota2',
    )
    quota3_records = scheduled_slots_tools.get_scheduled_quota(
        pgsql, 'some_quota3',
    )
    quota4_records = scheduled_slots_tools.get_scheduled_quota(
        pgsql, 'some_quota4',
    )

    assert quota1_records
    assert quota4_records
    assert len(quota2_records) + len(quota3_records) == 1


@pytest.mark.parametrize(
    'should_fail', (pytest.param([True]), pytest.param([False])),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_OUTDATED_CLEANUP={
        'work_interval_ms': 0,
        'operations': {'__default__': {'enabled': True}},
    },
)
async def test_worker_outdated_cleanup_errors_metric(
        taxi_driver_mode_subscription,
        testpoint,
        mockserver,
        taxi_driver_mode_subscription_monitor,
        should_fail,
):
    @testpoint('scheduled-slots-outdated-cleanup-worker-testpoint')
    def worker_testpoint(data):
        pass

    @testpoint(
        'scheduled-slots-outdated-cleanup-worker-testpoint-error-injection',
    )
    def _error_injection_testpoint(data):
        return {'inject_failure': True}

    metrics_before = await taxi_driver_mode_subscription_monitor.get_metric(
        'scheduled-slots-outdated-cleanup',
    )

    if should_fail:
        with pytest.raises(taxi_driver_mode_subscription.TestsuiteTaskFailed):
            await taxi_driver_mode_subscription.run_distlock_task(
                'scheduled-slots-outdated-cleanup',
            )
    else:
        await taxi_driver_mode_subscription.run_distlock_task(
            'scheduled-slots-outdated-cleanup',
        )

    await worker_testpoint.wait_call()

    metrics_after = await taxi_driver_mode_subscription_monitor.get_metric(
        'scheduled-slots-outdated-cleanup',
    )

    expected_successes = 0 if should_fail else 1
    expected_errors = 1 if should_fail else 0

    assert (
        expected_successes
        == metrics_after['successes'] - metrics_before['successes']
    )
    assert (
        expected_errors == metrics_after['errors'] - metrics_before['errors']
    )


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS_OUTDATED_CLEANUP={
        'work_interval_ms': 0,
        'operations': {
            '__default__': {'enabled': False},
            'cleanup_scheduled_slots_abandoned_meta': {
                'enabled': True,
                'delay_s': 1800,  # 0.5h
                'chunk_size': 1,
            },
        },
    },
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_slot_meta_query(
            _SLOT_ID_1.hex,
            dt.datetime(2020, 4, 4, 4, 30, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 1, 1, 3, 30, tzinfo=dt.timezone.utc),
        ),  # closed_at != NULL - should stay
        scheduled_slots_tools.make_insert_slot_meta_query(
            _SLOT_ID_2.hex,
            None,
            dt.datetime(2020, 4, 4, 4, 45, tzinfo=dt.timezone.utc),
        ),  # should stay - created_at not in delay
        scheduled_slots_tools.make_insert_slot_meta_query(
            _SLOT_ID_3.hex,
            None,
            dt.datetime(2020, 1, 1, 3, 30, tzinfo=dt.timezone.utc),
        ),  # should be deleted
        scheduled_slots_tools.make_insert_slot_meta_query(
            _SLOT_ID_4.hex,
            None,
            dt.datetime(2020, 1, 1, 3, 30, tzinfo=dt.timezone.utc),
        ),  # There will be slot - should stay
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_4.hex,
            'some_mode',
            _OFFER_IDENTITY_4,
            dt.datetime(2020, 4, 4, 2, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 3, 30, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_outdated_cleanup_abandoned_meta(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
):
    @testpoint('scheduled-slots-outdated-cleanup-worker-testpoint')
    def worker_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_distlock_task(
        'scheduled-slots-outdated-cleanup',
    )

    await worker_testpoint.wait_call()

    assert (
        len(
            scheduled_slots_tools.get_scheduled_slots_meta(
                pgsql, _SLOT_ID_1.hex,
            ),
        )
        == 1
    )

    assert (
        len(
            scheduled_slots_tools.get_scheduled_slots_meta(
                pgsql, _SLOT_ID_2.hex,
            ),
        )
        == 1
    )

    assert not scheduled_slots_tools.get_scheduled_slots_meta(
        pgsql, _SLOT_ID_3.hex,
    )

    assert (
        len(
            scheduled_slots_tools.get_scheduled_slots_meta(
                pgsql, _SLOT_ID_4.hex,
            ),
        )
        == 1
    )
