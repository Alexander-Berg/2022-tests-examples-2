# pylint: disable=import-only-modules
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


def generate_error_payload(task_id, allowed, error):
    return {
        'task_id': task_id,
        'new_state': 'error',
        'policy_allowed': allowed,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
        'error_string': error,
    }


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
async def test_succesfull_report_task_simple(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.status == 200

    payload = generate_payload(1000, 139)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    task_in_progress = select_columns_from_table(
        'crm_scheduler.task_pool_crm_policy_in_process',
        ['id', 'scope_start', 'scope_end'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert task_in_progress == [
        {'id': 1001, 'scope_start': [401], 'scope_end': [800]},
    ]

    task_finished = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['id', 'scope_start', 'scope_end', 'payload_int'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert task_finished == [
        {
            'id': 1000,
            'scope_start': [1],
            'scope_end': [400],
            'payload_int': 139,
        },
    ]


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
        'register_campaign.sql',
    ],
)
async def test_polcy_and_push_generated_and_reported(
        taxi_crm_scheduler, pgsql,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.status == 200

    payload = generate_payload(1000, 139)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    sending_runtime = select_columns_from_table(
        'crm_scheduler.sendings_runtime',
        [
            'sending_id_id',
            'policy_summ_success',
            'policy_summ_failed',
            'policy_fail_messages',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sending_runtime == [
        {
            'sending_id_id': 1,
            'policy_summ_success': 400,
            'policy_summ_failed': 0,
            'policy_fail_messages': [],
        },
    ]

    payload = generate_payload(1001, 350)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    sending_runtime = select_columns_from_table(
        'crm_scheduler.sendings_runtime',
        [
            'sending_id_id',
            'policy_summ_success',
            'policy_summ_failed',
            'policy_fail_messages',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sending_runtime == [
        {
            'sending_id_id': 1,
            'policy_summ_success': 800,
            'policy_summ_failed': 0,
            'policy_fail_messages': [],
        },
    ]

    payload = generate_payload(1002, 350)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_payload(1003, 350)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 8):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1031, 1000)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    sending_runtime = select_columns_from_table(
        'crm_scheduler.sendings_runtime',
        [
            'sending_id_id',
            'send_to_channel_success',
            'send_to_channel_failed',
            'send_fail_messages',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sending_runtime == [
        {
            'sending_id_id': 1,
            'send_to_channel_success': 1000,
            'send_to_channel_failed': 0,
            'send_fail_messages': [],
        },
    ]

    task_in_progress = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'sending_id_id',
            'size',
            'last_job_task_type_id',
            'payload_int',
            'processed',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert task_in_progress == [
        {
            'sending_id_id': 1,
            'size': [400],
            'last_job_task_type_id': 1,
            'payload_int': 139,
            'processed': 139,
        },
        {
            'sending_id_id': 1,
            'size': [400],
            'last_job_task_type_id': 1,
            'payload_int': 350,
            'processed': 350,
        },
        {
            'sending_id_id': 1,
            'size': [400],
            'last_job_task_type_id': 1,
            'payload_int': 350,
            'processed': 350,
        },
        {
            'sending_id_id': 1,
            'size': [400],
            'last_job_task_type_id': 1,
            'payload_int': 350,
            'processed': 161,
        },
        {
            'sending_id_id': 1,
            'size': [139, 350, 350, 161],
            'last_job_task_type_id': 13,
            'payload_int': 1000,
            'processed': -1,
        },
    ]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
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
async def test_log_tasks_generation_and_report(taxi_crm_scheduler, pgsql):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # emit all policy tasks
    await v1_get_task_list(taxi_crm_scheduler)

    # report at least 6 from them to be able to emit log
    for task_id, allowed in enumerate((200, 200, 200, 200, 200, 200), 1000):
        payload = generate_payload(task_id, allowed=allowed)
        await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await v1_get_task_list(taxi_crm_scheduler, 'marker ')
    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
    assert response.json() == {
        'task_type': 'send_to_log',
        'task_list': [
            {
                'id': 1031,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [],
                'task_ids_to_log': [1000, 1001, 1002, 1003, 1004],
            },
        ],
    }
    for _ in range(5):
        await v1_get_task_list(taxi_crm_scheduler)

    payload = generate_payload(1031, 0)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    payload = generate_payload(1032, 0, 123)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    task_reported = select_columns_from_table(
        'crm_scheduler.task_reported_default '
        'WHERE last_job_task_type_id = '
        '(SELECT id from crm_scheduler.task_types where name =\'user_push\')',
        ['id', 'scope_start', 'scope_end', 'size'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert task_reported == [
        {
            'id': 1032,
            'scope_start': [1, 401, 801, 1201, 1601],
            'scope_end': [400, 800, 1200, 1600, 2000],
            'size': [200, 200, 200, 200, 200],
        },
    ]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 1,
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
async def test_policy_failed_and_reported(
        taxi_crm_scheduler, pgsql, taxi_crm_scheduler_monitor,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.status == 200

    payload = generate_error_payload(1000, 139, 'test_policy_fail')
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    sending_runtime = select_columns_from_table(
        'crm_scheduler.sendings_runtime',
        [
            'sending_id_id',
            'policy_summ_success',
            'policy_summ_failed',
            'policy_fail_messages',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sending_runtime == [
        {
            'sending_id_id': 1,
            'policy_summ_success': 0,
            'policy_summ_failed': 400,
            'policy_fail_messages': ['test_policy_fail'],
        },
    ]

    task_reported = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['sending_id_id', 'payload_int'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert task_reported == [{'sending_id_id': 1, 'payload_int': 0}]

    task_in_process = read_count(pgsql, 'task_pool_crm_policy_in_process')
    assert task_in_process == 0
    await taxi_crm_scheduler.run_periodic_task('monitor-periodic')
    metrics = await taxi_crm_scheduler_monitor.get_metric('monitor-component')
    assert metrics['tasks-policy-failed-precise']['user_push'] == 400


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'generate_sending_pre_finished.sql',
    ],
)
async def test_sending_finished_report_full(taxi_crm_scheduler, pgsql):
    payload = {
        'task_id': 1015,
        'new_state': 'ok',
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }

    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    task_reported = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['sending_id_id', 'payload_int'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert task_reported == []

    sendings_runtime = select_columns_from_table(
        'crm_scheduler.sendings_runtime', ['*'], pgsql['crm_scheduler'], 1000,
    )
    assert sendings_runtime == []

    sendings_task_pool = select_columns_from_table(
        'crm_scheduler.task_pool_sending_finished',
        ['*'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings_task_pool == []

    sending_finished = select_columns_from_table(
        'crm_scheduler.sendings_finished',
        [
            'id',
            'sending_id',
            'campaign_id',
            'size',
            'policy_enabled',
            'send_enabled',
            'successfull',
            'error',
            'error_details',
            'force_stopped',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sending_finished == [
        {
            'id': 1,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'size': 3300,
            'policy_enabled': True,
            'send_enabled': True,
            'successfull': True,
            'error': None,
            'error_details': [],
            'force_stopped': False,
        },
    ]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'generate_sending_pre_finished_with_errors.sql',
    ],
)
async def test_sending_finished_with_some_errors(taxi_crm_scheduler, pgsql):
    # generate sending_finished_task
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    generated_task = select_columns_from_table(
        'crm_scheduler.task_pool_sending_finished',
        [
            'id',
            'sending_id',
            'successfull',
            'error',
            'error_details',
            'task_received',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert generated_task == [
        {
            'id': 1000,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': True,
            'error': 'have some issues',
            'error_details': [
                'Policy error: error_test1',
                'Send to channel error: error_test2',
                'logs error: error_test3',
            ],
            'task_received': False,
        },
    ]

    for _ in range(1, 5):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.json() == {
        'task_type': 'sending_finished',
        'task_list': [],
        'sending_finished_info': {
            'id': 1000,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': True,
            'error': 'have some issues',
            'error_detail': [
                'Policy error: error_test1',
                'Send to channel error: error_test2',
                'logs error: error_test3',
            ],
        },
    }

    payload = {
        'task_id': 1000,
        'new_state': 'ok',
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }

    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    finished_task = select_columns_from_table(
        'crm_scheduler.sendings_finished',
        [
            'id',
            'sending_id',
            'campaign_id',
            'size',
            'policy_enabled',
            'send_enabled',
            'successfull',
            'error',
            'error_details',
            'force_stopped',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert finished_task == [
        {
            'id': 1,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'size': 3300,
            'policy_enabled': True,
            'send_enabled': True,
            'successfull': True,
            'error': 'have some issues',
            'error_details': [
                'Policy error: error_test1',
                'Send to channel error: error_test2',
                'logs error: error_test3',
            ],
            'force_stopped': False,
        },
    ]
    must_be_empty = select_columns_from_table(
        'crm_scheduler.task_pool_sending_finished',
        ['*'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert must_be_empty == []

    must_be_empty = select_columns_from_table(
        'crm_scheduler.sendings', ['*'], pgsql['crm_scheduler'], 1000,
    )
    assert must_be_empty == []

    must_be_empty = select_columns_from_table(
        'crm_scheduler.sendings_runtime', ['*'], pgsql['crm_scheduler'], 1000,
    )
    assert must_be_empty == []


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'generate_sending_pre_finished_with_errors.sql',
    ],
)
async def test_sending_finished_retry(taxi_crm_scheduler, pgsql, mocked_time):

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    # Skip to get sending_finished
    for _ in range(1, 11):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    mocked_time.sleep(500)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    retry_pg_state = select_columns_from_table(
        'crm_scheduler.task_pool_sending_finished',
        ['id', 'retry_count', 'task_received'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert retry_pg_state == [
        {'id': 1000, 'retry_count': 1, 'task_received': False},
    ]

    for _ in range(1, 11):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    retry_pg_state = select_columns_from_table(
        'crm_scheduler.task_pool_sending_finished',
        ['id', 'retry_count', 'task_received'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert retry_pg_state == [
        {'id': 1000, 'retry_count': 1, 'task_received': True},
    ]


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'generate_sending_pre_finished_with_errors.sql',
        'add_logs_in_process_tasks.sql',
    ],
)
async def test_logs_confilct_resolved(taxi_crm_scheduler, pgsql, mocked_time):

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    # Skip to get sending_finished
    for _ in range(1, 11):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    logs_tasks = read_count(pgsql, 'task_pool_logs_in_process')
    assert logs_tasks == 1

    payload = {
        'task_id': 1000,
        'new_state': 'ok',
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }

    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    logs_tasks = read_count(pgsql, 'task_pool_logs_in_process')
    assert logs_tasks == 1

    payload = {
        'task_id': 12312,
        'new_state': 'ok',
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }

    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    logs_tasks = read_count(pgsql, 'task_pool_logs_in_process')
    assert logs_tasks == 0
