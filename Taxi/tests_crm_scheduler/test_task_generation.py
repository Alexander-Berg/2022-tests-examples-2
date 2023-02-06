# pylint: disable=import-only-modules
# pylint: disable=C0302
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table
from tests_crm_scheduler.utils import v1_get_task_list


def generate_payload(task_id, allowed, logs_saved=0):
    return {
        'task_id': task_id,
        'new_state': 'ok',
        'policy_allowed': allowed,
        'logs_saved': logs_saved,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


@pytest.mark.config(
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_policy_and_push_generated(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.status == 200

    payload = generate_payload(1000, 139)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_payload(1001, 350)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_payload(1002, 350)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_payload(1003, 350)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_user_push') == 1

    for _ in range(1, 8):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.json() == {
        'task_type': 'send_to_channel',
        'task_list': [
            {
                'id': 1031,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {
                        'scope_start': 1,
                        'scope_end': 400,
                        'offset': 0,
                        'size': 139,
                    },
                    {
                        'scope_start': 401,
                        'scope_end': 800,
                        'offset': 0,
                        'size': 350,
                    },
                    {
                        'scope_start': 801,
                        'scope_end': 1200,
                        'offset': 0,
                        'size': 350,
                    },
                    {
                        'scope_start': 1201,
                        'scope_end': 1600,
                        'offset': 0,
                        'size': 161,
                    },
                ],
            },
        ],
    }

    task_in_progress = select_columns_from_table(
        'crm_scheduler.task_pool_user_push_in_process',
        ['id', 'scope_start', 'size'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert task_in_progress == [
        {
            'id': 1031,
            'scope_start': [1, 401, 801, 1201],
            'size': [139, 350, 350, 161],
        },
    ]

    assert read_count(pgsql, 'task_pool_user_push_in_process') == 1


@pytest.mark.config(
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_timeot_restart(taxi_crm_scheduler, pgsql, mocked_time):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
    assert response.status == 200

    assert read_count(pgsql, 'task_pool_crm_policy_in_process') == 20
    assert read_count(pgsql, 'task_pool_crm_policy') == 11

    mocked_time.sleep(500)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_crm_policy_in_process') == 0
    assert read_count(pgsql, 'task_pool_crm_policy') == 31


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign_small.sql',
    ],
)
async def test_generate_right_push_tasks(
        taxi_crm_scheduler, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await v1_get_task_list(taxi_crm_scheduler)

    assert read_count(pgsql, 'task_pool_crm_policy_in_process') == 9

    for task_id in range(1000, 1008):
        payload = generate_payload(task_id, 400)
        await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    generated_push_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_user_push',
        ['id, scope_start, scope_end, start_offset, size'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert generated_push_tasks == [
        {
            'id': 1009,
            'scope_start': [1, 401, 801],
            'scope_end': [400, 800, 1200],
            'start_offset': [0, 0, 0],
            'size': [400, 400, 200],
        },
        {
            'id': 1010,
            'scope_start': [801, 1201, 1601],
            'scope_end': [1200, 1600, 2000],
            'start_offset': [200, 0, 0],
            'size': [200, 400, 400],
        },
        {
            'id': 1011,
            'scope_start': [2001, 2401, 2801],
            'scope_end': [2400, 2800, 3200],
            'start_offset': [0, 0, 0],
            'size': [400, 400, 200],
        },
    ]

    reported_tasks = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['scope_start, scope_end, size, payload_int, processed'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported_tasks == [
        {
            'scope_start': [1],
            'scope_end': [400],
            'size': [400],
            'payload_int': 400,
            'processed': 400,
        },
        {
            'scope_start': [401],
            'scope_end': [800],
            'size': [400],
            'payload_int': 400,
            'processed': 400,
        },
        {
            'scope_start': [801],
            'scope_end': [1200],
            'size': [400],
            'payload_int': 400,
            'processed': 400,
        },
        {
            'scope_start': [1201],
            'scope_end': [1600],
            'size': [400],
            'payload_int': 400,
            'processed': 400,
        },
        {
            'scope_start': [1601],
            'scope_end': [2000],
            'size': [400],
            'payload_int': 400,
            'processed': 400,
        },
        {
            'scope_start': [2001],
            'scope_end': [2400],
            'size': [400],
            'payload_int': 400,
            'processed': 400,
        },
        {
            'scope_start': [2401],
            'scope_end': [2800],
            'size': [400],
            'payload_int': 400,
            'processed': 400,
        },
        {
            'scope_start': [2801],
            'scope_end': [3200],
            'size': [400],
            'payload_int': 400,
            'processed': 200,
        },
    ]

    mocked_time.sleep(150)
    # cleanup old completed tasks and complete last task
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    generated_push_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_user_push',
        ['id, scope_start, scope_end, start_offset, size'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert generated_push_tasks == [
        {
            'id': 1009,
            'scope_start': [1, 401, 801],
            'scope_end': [400, 800, 1200],
            'start_offset': [0, 0, 0],
            'size': [400, 400, 200],
        },
        {
            'id': 1010,
            'scope_start': [801, 1201, 1601],
            'scope_end': [1200, 1600, 2000],
            'start_offset': [200, 0, 0],
            'size': [200, 400, 400],
        },
        {
            'id': 1011,
            'scope_start': [2001, 2401, 2801],
            'scope_end': [2400, 2800, 3200],
            'start_offset': [0, 0, 0],
            'size': [400, 400, 200],
        },
        # We have extra log task between compared to v1 generation
        {
            'id': 1013,
            'scope_start': [2801],
            'scope_end': [3200],
            'start_offset': [200],
            'size': [200],
        },
    ]
    # for v2 generation we still have all tasks till next generation call
    assert read_count(pgsql, 'task_reported_default') == 8
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_reported_default') == 0


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
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
async def test_log_tasks_generation(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # Get range(1000, 1020) tasks
    await v1_get_task_list(taxi_crm_scheduler)

    # after scheduler have 5 reported crm-policy
    # tasks generator creates 1 log task
    for task_id in range(1000, 1005):
        payload = generate_payload(task_id, 100)
        await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    # Now generator creates log task and put it into pool
    assert read_count(pgsql, 'task_pool_logs') == 0
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_logs') == 1

    # Now we retrieve some more crm-policy tasks
    await v1_get_task_list(taxi_crm_scheduler)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_logs_in_process') == 0

    # Now we take log task from pool (scheduler moves it into *_process table)
    await v1_get_task_list(taxi_crm_scheduler)
    assert read_count(pgsql, 'task_pool_logs') == 0
    assert read_count(pgsql, 'task_pool_logs_in_process') == 1


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 3,
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
async def test_current_sending_rotation(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    log_task_count = select_columns_from_table(
        'crm_scheduler.generation_statuses '
        'WHERE name = \'crm_policy_default\'',
        ['sending_id_to_use'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert log_task_count == [{'sending_id_to_use': 1}]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign_small.sql',
    ],
)
async def test_sending_finished_task_generation(
        taxi_crm_scheduler, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.status == 200

    for task_id, allowed in enumerate(
            (139, 139, 139, 139, 139, 139, 390, 0, 13), 1000,
    ):
        payload = generate_payload(task_id, allowed=allowed)
        response = await taxi_crm_scheduler.post(
            '/v1/report_task_ended', payload,
        )

    mocked_time.sleep(5000)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # emitted 2 send to channel and 2 log tasks
    for _ in range(7):
        await v1_get_task_list(taxi_crm_scheduler)

    # report policy log tasks
    payload = generate_payload(1009, 1)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1010, 1)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    # report send_to channel tasks
    payload = generate_payload(1011, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1012, 13)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # Skip to get log task
    for _ in range(1, 10):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
        if response.json()['task_type'] == 'send_to_log':
            break

    assert response.json() == {
        'task_type': 'send_to_log',
        'task_list': [
            {
                'id': 1013,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [],
                'task_ids_to_log': [1011],
            },
        ],
    }

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    push_wait_count = read_count(pgsql, 'task_reported_default')
    assert push_wait_count == 1

    payload = generate_payload(1013, 0)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    assert read_count(pgsql, 'task_reported_default') == 2
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 1
    mocked_time.sleep(5000)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # Skip to get log task
    for _ in range(14):
        await v1_get_task_list(taxi_crm_scheduler)

    payload = generate_payload(1014, 0, 100)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    # cleanup + generate sending finished
    assert read_count(pgsql, 'task_reported_default') == 1
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_reported_default') == 0
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    task_sending_finished = select_columns_from_table(
        'crm_scheduler.task_pool_sending_finished',
        ['sending_id', 'task_received'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert task_sending_finished == [
        {
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'task_received': False,
        },
    ]

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
    assert response.json() == {
        'task_type': 'sending_finished',
        'task_list': [],
        'sending_finished_info': {
            'id': 1015,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': True,
            'error_detail': [],
        },
    }

    payload = {
        'task_id': 1015,
        'new_state': 'ok',
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    sending_finished_result = select_columns_from_table(
        'crm_scheduler.sendings_finished',
        ['sending_id', 'successfull'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sending_finished_result == [
        {
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': True,
        },
    ]


@pytest.mark.config(
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
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_sending_zero_size.sql',
    ],
)
async def test_zero_size_sending(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 14):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1000, 0)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    finished_sendings = read_count(pgsql, 'sendings_finished')
    assert finished_sendings == 1


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_WORK_MODE={
        'generation_enabled': False,
        'task_emit_enabled': False,
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
async def test_generation_disabled(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    task_logs = read_count(pgsql, 'task_pool_crm_policy')
    assert task_logs == 0


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 1,
        'policy_allowance_in_seconds': 1000,
    },
    CRM_SCHEDULER_RESTART_TASKS_PARAMS_V5={
        'crm_policy': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'logs': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'driver_wall': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'driver_push': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'driver_sms': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'user_push': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'user_eda_sms': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'user_tags': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'eda_push': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'z_user_push': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'promo': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'counter_filter': {'retry_count': 2, 'timeout_interval_in_seconds': 1},
        'sending_finished': {
            'retry_count': 2,
            'timeout_interval_in_seconds': 1,
        },
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign_logs_only.sql',
    ],
)
@pytest.mark.skip(reason='Should be fixed in TAXICRMDEV-1927')
async def test_sending_finished_task_retry_error_fix(
        taxi_crm_scheduler, pgsql, mocked_time,
):
    # test for fixing TAXICRMDEV-1867 bug

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(3):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
        assert response.status == 200

    payload = generate_payload(1000, 0, 1)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    mocked_time.sleep(5000)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    task_sending_finished = select_columns_from_table(
        'crm_scheduler.task_pool_sending_finished',
        ['sending_id', 'task_received'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert task_sending_finished == [
        {
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'task_received': False,
        },
    ]

    # trying to get some retries
    for _ in range(10):
        mocked_time.sleep(5000)
        await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    task_sending_finished = select_columns_from_table(
        'crm_scheduler.task_pool_sending_finished',
        ['sending_id', 'task_received'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert task_sending_finished == []

    sending_finished_result = select_columns_from_table(
        'crm_scheduler.sendings_finished',
        ['sending_id', 'successfull'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert sending_finished_result == [
        {
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': False,
        },
    ]
