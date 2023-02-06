# pylint: disable=import-only-modules
import datetime

import pytest

from tests_crm_scheduler.utils import select_columns_from_table


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 15,
        'workers_period_in_seconds': 6,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
        'priority_for_test_tasks': 'very_high',
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_api_v1_generate_with_high_priority(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2021, 12, 15, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 1000000,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'channel_type': 'user_push',
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'is_test_sending': False,
        },
    )
    await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 1000000,
            'sending_id': '2d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'channel_type': 'user_push',
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'is_test_sending': True,
        },
    )
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    policy_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_crm_policy '
        'group by sending_id_id '
        'order by sending_id_id',
        ['sending_id_id, count(id)'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert policy_tasks == [
        {'sending_id_id': 1, 'count': 6},
        {'sending_id_id': 2, 'count': 23},
    ]


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 15,
        'workers_period_in_seconds': 6,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
        'priority_for_test_tasks': 'very_high',
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_api_v2_generate_with_high_priority(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2021, 12, 15, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 1000000,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
            'is_test_sending': False,
        },
    )
    await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 1000000,
            'sending_id': '2d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
            'is_test_sending': True,
        },
    )
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    mocked_time.sleep(500)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    policy_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_crm_policy '
        'group by sending_id_id '
        'order by sending_id_id',
        ['sending_id_id, count(id)'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert policy_tasks == [
        {'sending_id_id': 1, 'count': 6},
        {'sending_id_id': 2, 'count': 23},
    ]
