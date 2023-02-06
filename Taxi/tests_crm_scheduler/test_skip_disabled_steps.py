# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table

SENDING_ID_FIRST = '7d27b35a-0032-11ec-9a03-0242ac130003'
SENDING_ID_SECOND = '7d27b34a-0032-11ec-9a03-0242ac130003'


def generate_payload(sending_id, task_id, allowed):
    return {
        'task_id': task_id,
        'new_state': 'ok',
        'policy_allowed': allowed,
        'sending_id': sending_id,
    }


@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign_and_skip_send_campaign.sql',
    ],
)
async def test_send_enabled_is_worked(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    # Check if all policy tasks generated
    task_in_pool = select_columns_from_table(
        'crm_scheduler.task_pool_crm_policy_in_process',
        ['id', 'sending_id_id', 'scope_start'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert task_in_pool == [
        {'id': 1000, 'sending_id_id': 1, 'scope_start': [1]},
        {'id': 1001, 'sending_id_id': 1, 'scope_start': [401]},
        {'id': 1002, 'sending_id_id': 1, 'scope_start': [801]},
        {'id': 1003, 'sending_id_id': 1, 'scope_start': [1201]},
        {'id': 1004, 'sending_id_id': 2, 'scope_start': [1]},
        {'id': 1005, 'sending_id_id': 2, 'scope_start': [401]},
        {'id': 1006, 'sending_id_id': 2, 'scope_start': [801]},
        {'id': 1007, 'sending_id_id': 2, 'scope_start': [1201]},
    ]

    assert response.status == 200

    # Register couple policy tasks from both sendings
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(SENDING_ID_FIRST, 1000, 139),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(SENDING_ID_FIRST, 1001, 350),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended',
        generate_payload(SENDING_ID_SECOND, 1004, 350),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended',
        generate_payload(SENDING_ID_SECOND, 1005, 350),
    )

    just_reported_task = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'sending_id_id',
            'scope_start',
            'payload_int',
            'last_job_task_type_id',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert just_reported_task == [
        {
            'sending_id_id': 1,
            'scope_start': [1],
            'payload_int': 139,
            'last_job_task_type_id': 1,
        },
        {
            'sending_id_id': 1,
            'scope_start': [401],
            'payload_int': 350,
            'last_job_task_type_id': 1,
        },
        {
            'sending_id_id': 2,
            'scope_start': [1],
            'payload_int': 350,
            'last_job_task_type_id': 1,
        },
        {
            'sending_id_id': 2,
            'scope_start': [401],
            'payload_int': 350,
            'last_job_task_type_id': 1,
        },
    ]

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    reported_task_after_generation = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'sending_id_id',
            'scope_start',
            'payload_int',
            'last_job_task_type_id',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    # Check that task skip send step
    assert reported_task_after_generation == [
        {
            'sending_id_id': 1,
            'scope_start': [1],
            'payload_int': 139,
            'last_job_task_type_id': 1,
        },
        {
            'sending_id_id': 1,
            'scope_start': [401],
            'payload_int': 350,
            'last_job_task_type_id': 1,
        },
        {
            'sending_id_id': 2,
            'scope_start': [1],
            'payload_int': 350,
            'last_job_task_type_id': 13,
        },
        {
            'sending_id_id': 2,
            'scope_start': [401],
            'payload_int': 350,
            'last_job_task_type_id': 13,
        },
    ]

    # Register leftovers tasks
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(SENDING_ID_FIRST, 1002, 239),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(SENDING_ID_FIRST, 1003, 30),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended',
        generate_payload(SENDING_ID_SECOND, 1006, 350),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(SENDING_ID_SECOND, 1007, 20),
    )

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    log_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_logs',
        ['sending_id_id', 'scope_start', 'size'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert log_tasks == [
        {'sending_id_id': 2, 'scope_start': None, 'size': None},
    ]


@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign_and_skip_policy_campaign.sql',
    ],
)
async def test_policy_disable_is_worked(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.post('/v1/get_task_list', {})  # policy
    for _ in range(1, 8):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    # check that push tasks generated and recieved
    assert response.json() == {
        'task_type': 'send_to_channel',
        'task_list': [
            {
                'id': 1004,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1,
                        'scope_end': 1000,
                        'offset': 0,
                        'size': 1000,
                    },
                ],
            },
            {
                'id': 1005,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1001,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 230,
                    },
                ],
            },
        ],
    }
    policy_tasks = read_count(pgsql, 'task_pool_crm_policy')
    policy_tasks_in_process = read_count(
        pgsql, 'task_pool_crm_policy_in_process',
    )

    assert policy_tasks == 0
    # tasks by default campaign and have not skipped tasks
    assert policy_tasks_in_process == 4


@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign_and_skip_policy_send_campaign.sql',
    ],
)
async def test_policy_and_send_disable_is_worked(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})  # policy
    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})  # policy
    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})  # logs

    assert {
        'task_type': 'send_to_log',
        'task_list': [
            {
                'id': 1004,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1,
                        'scope_end': 1000,
                        'offset': 0,
                        'size': 1000,
                    },
                ],
            },
            {
                'id': 1005,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1001,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 230,
                    },
                ],
            },
            {
                'id': 1006,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1230,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 1,
                    },
                ],
            },
            {
                'id': 1007,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1230,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 1,
                    },
                ],
            },
            {
                'id': 1008,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1230,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 1,
                    },
                ],
            },
            {
                'id': 1009,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1230,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 1,
                    },
                ],
            },
            {
                'id': 1010,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1230,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 1,
                    },
                ],
            },
            {
                'id': 1011,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1230,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 1,
                    },
                ],
            },
            {
                'id': 1012,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1230,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 1,
                    },
                ],
            },
            {
                'id': 1013,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1230,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 1,
                    },
                ],
            },
        ],
    }

    # check that logs tasks generated and recieved
    assert response.json() == {
        'task_type': 'send_to_log',
        'task_list': [
            {
                'id': 1004,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1,
                        'scope_end': 1000,
                        'offset': 0,
                        'size': 1000,
                    },
                ],
            },
            {
                'id': 1005,
                'sending_id': '7d27b34a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1001,
                        'scope_end': 1230,
                        'offset': 0,
                        'size': 230,
                    },
                ],
            },
        ],
    }
    policy_tasks = read_count(pgsql, 'task_pool_crm_policy')
    policy_tasks_in_process = read_count(
        pgsql, 'task_pool_crm_policy_in_process',
    )
    push_tasks = read_count(pgsql, 'task_pool_user_push')
    push_tasks_in_process = read_count(pgsql, 'task_pool_user_push_in_process')

    assert policy_tasks == 0
    # tasks by default campaign and have not skipped tasks
    assert policy_tasks_in_process == 4
    assert push_tasks == 0
    assert push_tasks_in_process == 0
