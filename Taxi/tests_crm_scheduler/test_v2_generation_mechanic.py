# pylint: disable=import-only-modules
import datetime

import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_sending.sql',
    ],
)
async def test_generation_policy(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    policy_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_crm_policy',
        ['step_num', 'source_task_ids'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert policy_tasks == [
        {'step_num': 1, 'source_task_ids': []},
        {'step_num': 1, 'source_task_ids': []},
        {'step_num': 1, 'source_task_ids': []},
        {'step_num': 1, 'source_task_ids': []},
    ]


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_register_sending_v1(
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
            'size': 12300,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'channel_type': 'user_push',
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
        },
    )
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        ['generation_version'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert sendings == [{'generation_version': 2}]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_sending.sql',
        'add_leftover_reported_policy_tasks.sql',
    ],
)
async def test_check_leftover_log_generation(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    assert read_count(pgsql, 'task_pool_logs') == 0
    assert (
        read_count(pgsql, 'task_reported_default', 'logs_generated = True')
        == 0
    )

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_logs') == 1
    assert (
        read_count(pgsql, 'task_reported_default', 'logs_generated = True')
        == 3
    )

    mocked_time.sleep(100500)

    # here generated last leftover task && send task after wait period
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_logs') == 2
    assert (
        read_count(pgsql, 'task_reported_default', 'logs_generated = True')
        == 4
    )

    # cleanup here
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert (
        read_count(pgsql, 'task_reported_default', 'logs_generated = True')
        == 0
    )

    log_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_logs',
        ['step_num', 'task_ids_to_log'],
        pgsql['crm_scheduler'],
        1,
    )

    assert log_tasks == [
        {'step_num': 4, 'task_ids_to_log': [1000, 1001, 1002]},
    ]


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 2,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
# @conftest.crm_admin_get_list_mock()
async def test_register_sending_v2(
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
            'size': 12300,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            'channel_type': 'user_push',
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
        },
    )
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        ['generation_version'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == [{'generation_version': 2}]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_sending_finished_first_step.sql',
        'add_reported_policy_tasks.sql',
    ],
)
async def test_generation_send_to_channel(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    # Generate first task by bulk filled
    assert read_count(pgsql, 'task_pool_eda_push') == 1
    mocked_time.sleep(100500)
    # Generate first task by wait period
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_eda_push') == 2
    eda_push_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_eda_push',
        ['start_offset', 'size', 'source_task_ids', 'step_num'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert eda_push_tasks == [
        {
            'start_offset': [0, 0, 0, 0],
            'size': [123, 398, 212, 267],
            'source_task_ids': [1000, 1001, 1002, 1003],
            'step_num': 2,
        },
        {
            'start_offset': [267],
            'size': [133],
            'source_task_ids': [1003],
            'step_num': 2,
        },
    ]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_sending_skip_log.sql',
        'add_leftover_reported_policy_tasks.sql',
    ],
)
async def test_skip_logs(taxi_crm_scheduler, mockserver, pgsql, mocked_time):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    assert read_count(pgsql, 'task_pool_logs') == 0
    assert (
        read_count(pgsql, 'task_reported_default', 'logs_generated = True')
        == 0
    )

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_logs') == 0
    assert (
        read_count(pgsql, 'task_reported_default', 'logs_generated = False')
        == 4
    )

    mocked_time.sleep(100500)

    # here generated last leftover task && send task after wait period
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_logs') == 0
    assert (
        read_count(pgsql, 'task_reported_default', 'logs_generated = False')
        == 4
    )

    # cleanup here
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert (
        read_count(pgsql, 'task_reported_default', 'logs_generated = False')
        == 0
    )

    log_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_logs',
        ['step_num', 'task_ids_to_log'],
        pgsql['crm_scheduler'],
        1,
    )

    assert log_tasks == []


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_sending_finished_first_step.sql',
        'add_final_step_generation.sql',
    ],
)
async def test_final_step_generation(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    assert read_count(pgsql, 'task_pool_logs') == 0

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_logs') == 1

    mocked_time.sleep(100500)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_logs') == 2

    # cleanup here
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 0

    log_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_logs',
        ['step_num', 'source_task_ids', 'size', 'start_offset'],
        pgsql['crm_scheduler'],
        100,
    )

    assert log_tasks == [
        {
            'step_num': 4,
            'source_task_ids': [1004],
            'size': [1000],
            'start_offset': [0],
        },
        {
            'step_num': 4,
            'source_task_ids': [1005],
            'size': [133],
            'start_offset': [0],
        },
    ]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_sending_finished_first_step.sql',
    ],
)
async def test_sending_finished_generation(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    sending_finished = select_columns_from_table(
        'crm_scheduler.task_pool_sending_finished',
        ['sending_id', 'task_received'],
        pgsql['crm_scheduler'],
        100,
    )
    assert sending_finished == [
        {
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'task_received': False,
        },
    ]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_only_one_step_sending_policy.sql',
    ],
)
async def test_one_step_sending_1(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    sendings_generated = select_columns_from_table(
        'crm_scheduler.sendings',
        ['last_first_step_generated'],
        pgsql['crm_scheduler'],
        100,
    )

    assert read_count(pgsql, 'task_pool_crm_policy') == 4
    assert sendings_generated == [{'last_first_step_generated': 1230}]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_only_one_step_sending_channel.sql',
    ],
)
async def test_one_step_sending_2(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    sendings_generated = select_columns_from_table(
        'crm_scheduler.sendings',
        ['last_first_step_generated'],
        pgsql['crm_scheduler'],
        100,
    )

    assert read_count(pgsql, 'task_pool_driver_wall') == 2
    assert sendings_generated == [{'last_first_step_generated': 1230}]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_only_one_step_sending_logs.sql',
    ],
)
async def test_one_step_sending_3(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    sendings_generated = select_columns_from_table(
        'crm_scheduler.sendings',
        ['last_first_step_generated'],
        pgsql['crm_scheduler'],
        100,
    )

    assert read_count(pgsql, 'task_pool_logs') == 2
    assert sendings_generated == [{'last_first_step_generated': 1230}]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_sending_finished_first_step.sql',
        'add_reported_big_policy_tasks.sql',
    ],
)
async def test_small_channels_tasks(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    mocked_time.sleep(100500)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    eda_push_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_eda_push',
        ['start_offset, size , step_num, source_task_ids'],
        pgsql['crm_scheduler'],
        100,
    )
    assert eda_push_tasks == [
        {
            'start_offset': [0],
            'size': [1000],
            'step_num': 2,
            'source_task_ids': [1000],
        },
        {
            'start_offset': [1000],
            'size': [1000],
            'step_num': 2,
            'source_task_ids': [1000],
        },
        {
            'start_offset': [2000],
            'size': [1000],
            'step_num': 2,
            'source_task_ids': [1000],
        },
        {
            'start_offset': [3000, 0],
            'size': [567, 433],
            'step_num': 2,
            'source_task_ids': [1000, 1001],
        },
        {
            'start_offset': [433],
            'size': [1000],
            'step_num': 2,
            'source_task_ids': [1001],
        },
        {
            'start_offset': [1433],
            'size': [1000],
            'step_num': 2,
            'source_task_ids': [1001],
        },
        {
            'start_offset': [2433],
            'size': [881],
            'step_num': 2,
            'source_task_ids': [1001],
        },
    ]
