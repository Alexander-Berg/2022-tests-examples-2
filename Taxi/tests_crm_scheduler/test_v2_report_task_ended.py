# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table


def generate_payload(task_id, allowed, logs_saved):
    return (
        {
            'task_id': task_id,
            'new_state': 'ok',
            'filter_approved': allowed,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'logs_saved': logs_saved,
        }
        if logs_saved != 0
        else {
            'task_id': task_id,
            'new_state': 'ok',
            'filter_approved': allowed,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
        }
    )


async def report_compleated_task(
        taxi_crm_scheduler, task_id, num_filter_allowed, num_logs_saved=0,
):
    payload = generate_payload(task_id, num_filter_allowed, num_logs_saved)
    await taxi_crm_scheduler.post('/v2/report_task_ended', payload)


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
        'add_policy_tasks.sql',
    ],
)
async def test_report_policy_task(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await report_compleated_task(taxi_crm_scheduler, 1000, 123)
    await report_compleated_task(taxi_crm_scheduler, 1001, 323)

    reported = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'id',
            'scope_start',
            'scope_end',
            'start_offset',
            'size',
            'payload_int',
            'processed',
            'channel_to_send_name',
            'logs_generated',
            'step_num',
            'filter_approved',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported == [
        {
            'id': 1000,
            'scope_start': [1],
            'scope_end': [400],
            'start_offset': [0],
            'size': [400],
            'payload_int': 0,
            'processed': 0,
            'channel_to_send_name': None,
            'logs_generated': False,
            'step_num': 1,
            'filter_approved': 123,
        },
        {
            'id': 1001,
            'scope_start': [401],
            'scope_end': [800],
            'start_offset': [0],
            'size': [400],
            'payload_int': 0,
            'processed': 0,
            'channel_to_send_name': None,
            'logs_generated': False,
            'step_num': 1,
            'filter_approved': 323,
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
        'add_policy_sending.sql',
        'add_non_first_step_tasks.sql',
    ],
)
async def test_report_non_first_step_task(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await report_compleated_task(taxi_crm_scheduler, 1015, 1000)
    await report_compleated_task(taxi_crm_scheduler, 1016, 133)

    assert read_count(pgsql, 'task_reported_default') == 2

    reported = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'id',
            'sending_id_id',
            'last_job_task_type_id',
            'payload_int',
            'channel_to_send_name',
            'processed',
            'logs_generated',
            'step_num',
            'filter_approved',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported == [
        {
            'id': 1015,
            'sending_id_id': 1,
            'last_job_task_type_id': 16,
            'payload_int': 0,
            'channel_to_send_name': 'eda_push',
            'processed': 0,
            'logs_generated': False,
            'step_num': 2,
            'filter_approved': 1000,
        },
        {
            'id': 1016,
            'sending_id_id': 1,
            'last_job_task_type_id': 16,
            'payload_int': 0,
            'channel_to_send_name': 'eda_push',
            'processed': 0,
            'logs_generated': False,
            'step_num': 2,
            'filter_approved': 133,
        },
    ]

    mocked_time.sleep(100500)
    # Generate Next Send step
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_reported_default') == 2
    # cleanup
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_reported_default') == 0

    driver_wall_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_driver_wall',
        [
            'id',
            'sending_id_id',
            'step_num',
            'source_task_ids',
            'size',
            'start_offset',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert driver_wall_tasks == [
        {
            'id': 1000,
            'sending_id_id': 1,
            'step_num': 3,
            'source_task_ids': [1015],
            'size': [1000],
            'start_offset': [0],
        },
        {
            'id': 1001,
            'sending_id_id': 1,
            'step_num': 3,
            'source_task_ids': [1016],
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
        'add_policy_sending.sql',
        'add_logs_final_tasks.sql',
    ],
)
async def test_report_logs_last_tasks(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await report_compleated_task(taxi_crm_scheduler, 1019, 1000)
    await report_compleated_task(taxi_crm_scheduler, 1020, 133)

    assert read_count(pgsql, 'task_reported_default') == 2

    reported = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'id',
            'sending_id_id',
            'last_job_task_type_id',
            'payload_int',
            'channel_to_send_name',
            'processed',
            'logs_generated',
            'step_num',
            'filter_approved',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported == [
        {
            'id': 1019,
            'sending_id_id': 1,
            'last_job_task_type_id': 2,
            'payload_int': 0,
            'channel_to_send_name': None,
            'processed': 0,
            'logs_generated': False,
            'step_num': 4,
            'filter_approved': 1000,
        },
        {
            'id': 1020,
            'sending_id_id': 1,
            'last_job_task_type_id': 2,
            'payload_int': 0,
            'channel_to_send_name': None,
            'processed': 0,
            'logs_generated': False,
            'step_num': 4,
            'filter_approved': 133,
        },
    ]

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 0


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
        'add_only_policy_sending.sql',
        'add_only_policy_tasks.sql',
    ],
)
async def test_report_only_policy(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await report_compleated_task(taxi_crm_scheduler, 1000, 900)
    await report_compleated_task(taxi_crm_scheduler, 1001, 124)

    assert read_count(pgsql, 'task_reported_default') == 2

    reported = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'id',
            'sending_id_id',
            'last_job_task_type_id',
            'payload_int',
            'channel_to_send_name',
            'processed',
            'logs_generated',
            'step_num',
            'filter_approved',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported == [
        {
            'id': 1000,
            'sending_id_id': 1,
            'last_job_task_type_id': 1,
            'payload_int': 0,
            'channel_to_send_name': None,
            'processed': 0,
            'logs_generated': False,
            'step_num': 1,
            'filter_approved': 900,
        },
        {
            'id': 1001,
            'sending_id_id': 1,
            'last_job_task_type_id': 1,
            'payload_int': 0,
            'channel_to_send_name': None,
            'processed': 0,
            'logs_generated': False,
            'step_num': 1,
            'filter_approved': 124,
        },
    ]

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 0


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
        'add_only_channel_sending.sql',
        'add_only_channel_tasks.sql',
    ],
)
async def test_report_only_channel(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await report_compleated_task(taxi_crm_scheduler, 1000, 1000)
    await report_compleated_task(taxi_crm_scheduler, 1001, 230)

    assert read_count(pgsql, 'task_reported_default') == 2

    reported = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'id',
            'sending_id_id',
            'last_job_task_type_id',
            'payload_int',
            'channel_to_send_name',
            'processed',
            'logs_generated',
            'step_num',
            'filter_approved',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported == [
        {
            'id': 1000,
            'sending_id_id': 1,
            'last_job_task_type_id': 10,
            'payload_int': 0,
            'channel_to_send_name': 'driver_wall',
            'processed': 0,
            'logs_generated': False,
            'step_num': 1,
            'filter_approved': 1000,
        },
        {
            'id': 1001,
            'sending_id_id': 1,
            'last_job_task_type_id': 10,
            'payload_int': 0,
            'channel_to_send_name': 'driver_wall',
            'processed': 0,
            'logs_generated': False,
            'step_num': 1,
            'filter_approved': 230,
        },
    ]

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 0


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
        'add_only_logs_sending.sql',
        'add_only_logs_tasks.sql',
    ],
)
async def test_report_only_logs(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await report_compleated_task(taxi_crm_scheduler, 1000, 1000, 101)
    await report_compleated_task(taxi_crm_scheduler, 1001, 230, 202)

    assert read_count(pgsql, 'task_reported_default') == 2

    reported = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'id',
            'sending_id_id',
            'last_job_task_type_id',
            'payload_int',
            'channel_to_send_name',
            'processed',
            'logs_generated',
            'step_num',
            'filter_approved',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert reported == [
        {
            'id': 1000,
            'sending_id_id': 1,
            'last_job_task_type_id': 2,
            'payload_int': 0,
            'channel_to_send_name': None,
            'processed': 0,
            'logs_generated': False,
            'step_num': 1,
            'filter_approved': 1000,
        },
        {
            'id': 1001,
            'sending_id_id': 1,
            'last_job_task_type_id': 2,
            'payload_int': 0,
            'channel_to_send_name': None,
            'processed': 0,
            'logs_generated': False,
            'step_num': 1,
            'filter_approved': 230,
        },
    ]

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 0

    reported = select_columns_from_table(
        'crm_scheduler.sendings_runtime',
        ['logs_success'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert reported == [{'logs_success': 303}]


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
        'add_only_logs_sending.sql',
        'add_only_logs_tasks.sql',
    ],
)
async def test_logs_restart_1(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    error_payload = {
        'task_id': 1000,
        'new_state': 'error',
        'error_string': 'TEST ERROR',
        'filter_approved': 0,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }

    await taxi_crm_scheduler.post('/v2/report_task_ended', error_payload)

    await report_compleated_task(taxi_crm_scheduler, 1001, 230)

    task_logs = select_columns_from_table(
        'crm_scheduler.task_pool_logs',
        [
            'id',
            'sending_id_id',
            'scope_start',
            'scope_end',
            'start_offset',
            'size',
            'retry_count',
            'step_num',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert task_logs == [
        {
            'id': 1000,
            'sending_id_id': 1,
            'scope_start': [1],
            'scope_end': [1000],
            'start_offset': [0],
            'size': [1000],
            'retry_count': 1,
            'step_num': 1,
        },
    ]

    assert read_count(pgsql, 'task_reported_default') == 1


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
        'add_non_first_step_tasks.sql',
    ],
)
async def test_channel_error_reported(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    error_payload = {
        'task_id': 1015,
        'new_state': 'error',
        'error_string': 'TEST ERROR',
        'filter_approved': 0,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }

    await taxi_crm_scheduler.post('/v2/report_task_ended', error_payload)

    await report_compleated_task(taxi_crm_scheduler, 1016, 133)

    task_reported = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        [
            'id',
            'sending_id_id',
            'scope_start',
            'scope_end',
            'start_offset',
            'size',
            'filter_approved',
        ],
        pgsql['crm_scheduler'],
        1000,
    )

    assert task_reported == [
        {
            'id': 1015,
            'sending_id_id': 1,
            'scope_start': [],
            'scope_end': [],
            'start_offset': [0, 0, 0, 0],
            'size': [123, 398, 212, 267],
            'filter_approved': 0,
        },
        {
            'id': 1016,
            'sending_id_id': 1,
            'scope_start': [],
            'scope_end': [],
            'start_offset': [267],
            'size': [133],
            'filter_approved': 133,
        },
    ]
