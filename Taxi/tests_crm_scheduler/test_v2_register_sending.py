# pylint: disable=import-only-modules
import datetime

import pytest

from tests_crm_scheduler.utils import select_columns_from_table


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 1,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_generation_version_is_low(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
    )

    assert (
        response.json()['message']
        == 'Current allowed generation less than required!'
    )


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_wrong_channel_name(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_1push', 'driver_wall', 'logs'],
        },
    )

    assert response.json()['message'] == 'Unknown step task_type : eda_1push'


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_wrong_order_policy(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['eda_push', 'crm_policy', 'driver_wall', 'logs'],
        },
    )

    assert (
        response.json()['message']
        == 'Policy step must be first if exists and only 1 is allowed'
    )


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_wrong_order_logs(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_push', 'logs', 'driver_wall'],
        },
    )

    assert (
        response.json()['message']
        == 'Logs step must be last if exists, and only 1 is allowed'
    )


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_too_many_policy_steps(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': [
                'crm_policy',
                'crm_policy',
                'eda_push',
                'driver_wall',
                'logs',
            ],
        },
    )

    assert (
        response.json()['message']
        == 'Policy step must be first if exists and only 1 is allowed'
    )


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_too_many_logs_steps(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs', 'logs'],
        },
    )

    assert (
        response.json()['message']
        == 'Logs step must be last if exists, and only 1 is allowed'
    )


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_wrong_policy_channel(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_walsl',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
    )

    assert response.json()['message'] == 'Policy channel name is invalid'


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_test_can_register_campaign_with_appropriate_time(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
    )
    assert response.status == 200
    assert response.json() == {}
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'group_id',
            'channel_id',
            'sending_id',
            'dependency_uuid',
            'steps',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == [
        {
            'campaign_id': '123',
            'group_id': '456',
            'channel_id': -1,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
    ]
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_cant_register_campaign_with_expired_time_if_checking_enabled(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2023, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
    )
    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Working time for communication with campaign=123 and group=456'
            ' has expired'
        ),
    }
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'group_id',
            'channel_id',
            'sending_id',
            'dependency_uuid',
            'steps',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == []
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': False,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_can_register_campaign_with_expired_time_if_checking_disabled(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2023, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
    )
    assert response.status == 200
    assert response.json() == {}
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'group_id',
            'channel_id',
            'sending_id',
            'dependency_uuid',
            'steps',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == [
        {
            'campaign_id': '123',
            'group_id': '456',
            'channel_id': -1,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
        },
    ]
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')


@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_special_requirements_for_testing_sending(
        # We can register testing sending even if it's expired
        # also log step is being cleared for v2 api.
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    now = datetime.datetime(2023, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_wall',
            'steps': ['crm_policy', 'eda_push', 'driver_wall', 'logs'],
            'is_test_sending': True,
        },
    )
    assert response.status == 200
    assert response.json() == {}
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'campaign_id',
            'group_id',
            'channel_id',
            'sending_id',
            'dependency_uuid',
            'steps',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == [
        {
            'campaign_id': '123',
            'group_id': '456',
            'channel_id': -1,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'steps': ['crm_policy', 'eda_push', 'driver_wall'],
        },
    ]
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
