# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 2,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 1,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_succesfull_get_list_simple(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.status == 200

    assert response.json() == {
        'task_type': 'check_crm_policy',
        'task_list': [
            {
                'id': 1000,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1,
                        'scope_end': 400,
                        'offset': 0,
                        'size': 400,
                    },
                ],
            },
            {
                'id': 1001,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 401,
                        'scope_end': 800,
                        'offset': 0,
                        'size': 400,
                    },
                ],
            },
        ],
    }


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 1,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 1,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_succesfull_get_list_simple2(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.status == 200

    assert response.json() == {
        'task_type': 'check_crm_policy',
        'task_list': [
            {
                'id': 1000,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1,
                        'scope_end': 400,
                        'offset': 0,
                        'size': 400,
                    },
                ],
            },
        ],
    }
    response2 = await taxi_crm_scheduler.post('/v1/get_task_list', {})
    assert response2.json() == {
        'task_type': 'check_crm_policy',
        'task_list': [
            {
                'id': 1001,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 401,
                        'scope_end': 800,
                        'offset': 0,
                        'size': 400,
                    },
                ],
            },
        ],
    }

    response3 = await taxi_crm_scheduler.post('/v1/get_task_list', {})
    assert response3.json() == {'task_type': 'idle', 'task_list': []}

    task_in_progress = select_columns_from_table(
        'crm_scheduler.task_pool_crm_policy_in_process',
        ['id', 'scope_start', 'scope_end'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert task_in_progress == [
        {'id': 1000, 'scope_start': [1], 'scope_end': [400]},
        {'id': 1001, 'scope_start': [401], 'scope_end': [800]},
    ]


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
                        'task_emit_enabled_for_v1': False,
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
                        'task_emit_enabled_for_v1': True,
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
        'register_campaign.sql',
    ],
)
async def test_emit_disabled(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    task_logs = read_count(pgsql, 'task_pool_crm_policy')
    assert task_logs == 31

    emmiter_state_before = select_columns_from_table(
        'crm_scheduler.emitter_task_state',
        ['lock', 'last_task_type_id', 'task_thread_emitted'],
        pgsql['crm_scheduler'],
        1,
    )

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

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
