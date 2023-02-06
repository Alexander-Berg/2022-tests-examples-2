# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table


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
        'add_policy_sending.sql',
        'add_policy_tasks.sql',
    ],
)
async def test_get_task_list_policy(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'filter_step',
        'task_list': [
            {
                'id': 1000,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 1, 'scope_end': 400}],
                'step_num': 1,
            },
            {
                'id': 1001,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 401, 'scope_end': 800}],
                'step_num': 1,
            },
            {
                'id': 1002,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 801, 'scope_end': 1200}],
                'step_num': 1,
            },
            {
                'id': 1003,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 1201, 'scope_end': 1230}],
                'step_num': 1,
            },
        ],
    }


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
        'add_policy_sending.sql',
        'add_leftoverlogs_tasks.sql',
    ],
)
async def test_get_leftover_log_tasks(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 4):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'pipe_step',
        'task_list': [
            {
                'id': 1000,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [],
                'step_num': 4,
                'task_ids_to_log': [1000, 1001, 1002],
            },
            {
                'id': 1001,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [],
                'step_num': 4,
                'task_ids_to_log': [1003],
            },
        ],
    }


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
        'add_policy_sending.sql',
        'add_non_first_step_tasks.sql',
    ],
)
async def test_get_non_first_step_task(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 12):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'pipe_step',
        'task_list': [
            {
                'id': 1015,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'source_task_id': 1000, 'offset': 0, 'size': 123},
                    {'source_task_id': 1001, 'offset': 0, 'size': 398},
                    {'source_task_id': 1002, 'offset': 0, 'size': 212},
                    {'source_task_id': 1003, 'offset': 0, 'size': 267},
                ],
                'step_num': 2,
            },
            {
                'id': 1016,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'source_task_id': 1003, 'offset': 267, 'size': 133},
                ],
                'step_num': 2,
            },
        ],
    }


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
        'add_policy_sending.sql',
        'add_logs_tasks.sql',
    ],
)
async def test_log_task(taxi_crm_scheduler, mockserver, pgsql, mocked_time):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 4):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'pipe_step',
        'task_list': [
            {
                'id': 1019,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 0, 'size': 1000, 'source_task_id': 1004},
                ],
                'step_num': 4,
            },
            {
                'id': 1020,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 0, 'size': 133, 'source_task_id': 1005},
                ],
                'step_num': 4,
            },
        ],
    }


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
        'add_policy_sending.sql',
        'add_sending_finished.sql',
    ],
)
async def test_sending_finished_successfull(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    for _ in range(1, 5):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'sending_finished',
        'task_list': [],
        'sending_finished_info': {
            'id': 1000,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': True,
            'error_detail': [],
        },
    }


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
        'add_only_policy_sending.sql',
        'add_only_policy_tasks.sql',
    ],
)
async def test_get_task_list_only_policy(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 4):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'pipe_step',
        'task_list': [
            {
                'id': 1019,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 1, 'scope_end': 1000}],
                'step_num': 1,
            },
            {
                'id': 1020,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 1001, 'scope_end': 1230}],
                'step_num': 1,
            },
        ],
    }


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
        'add_only_channel_sending.sql',
        'add_only_channel_tasks.sql',
    ],
)
async def test_get_task_list_only_channel(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 6):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'pipe_step',
        'task_list': [
            {
                'id': 1019,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 1, 'scope_end': 1000}],
                'step_num': 1,
            },
            {
                'id': 1020,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 1001, 'scope_end': 1230}],
                'step_num': 1,
            },
        ],
    }


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
        'add_only_logs_sending.sql',
        'add_only_logs_tasks.sql',
    ],
)
async def test_get_task_list_only_logs(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 4):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'pipe_step',
        'task_list': [
            {
                'id': 1019,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 1, 'scope_end': 1000}],
                'step_num': 1,
            },
            {
                'id': 1020,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [{'scope_start': 1001, 'scope_end': 1230}],
                'step_num': 1,
            },
        ],
    }


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    CRM_SCHEDULER_WORK_MODE={
                        'generation_enabled': True,
                        'task_emit_enabled': False,
                    },
                ),
            ],
            id='basic emit switch',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    CRM_SCHEDULER_WORK_MODE={
                        'generation_enabled': True,
                        'task_emit_enabled': True,
                        'task_emit_enabled_for_v2': False,
                    },
                ),
            ],
            id='specific switch for v1 api',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    CRM_SCHEDULER_WORK_MODE={
                        'generation_enabled': True,
                        'task_emit_enabled': False,
                        'task_emit_enabled_for_v2': True,
                    },
                ),
            ],
            id='general switch overrides specific one',
        ),
    ],
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'add_sending.sql',
    ],
)
async def test_emit_disabled(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    task_logs = read_count(pgsql, 'task_pool_crm_policy')
    assert task_logs == 4

    emmiter_state_before = select_columns_from_table(
        'crm_scheduler.emitter_task_state',
        ['lock', 'last_task_type_id', 'task_thread_emitted'],
        pgsql['crm_scheduler'],
        1,
    )

    response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    emmiter_state_after = select_columns_from_table(
        'crm_scheduler.emitter_task_state',
        ['lock', 'last_task_type_id', 'task_thread_emitted'],
        pgsql['crm_scheduler'],
        1,
    )

    # Check that emmiter state doesn't change
    # We need to check it to avoid races between
    # v1 and v2 api in case of disabled api handler
    assert emmiter_state_before == emmiter_state_after

    assert response.status == 200
    assert response.json() == {'task_type': 'idle', 'task_list': []}
