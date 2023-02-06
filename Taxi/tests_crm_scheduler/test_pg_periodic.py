# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table


def generate_payload(task_id, allowed, logs_saved=0):
    return {
        'task_id': task_id,
        'new_state': 'ok',
        'policy_allowed': allowed,
        'logs_saved': logs_saved,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


@pytest.mark.suspend_periodic_tasks('pg-rotate-tasks-history-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 2,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 1,
        'policy_allowance_in_seconds': 1000,
    },
)
async def test_log_rotated(taxi_crm_scheduler, pgsql, mocked_time):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    def get_logged_tasks(pgsql):
        return read_count(pgsql, 'log_task_generated')

    def get_logged_tasks_old(pgsql):
        return read_count(pgsql, 'log_task_generated_old')

    assert get_logged_tasks(pgsql) == 10

    await taxi_crm_scheduler.run_periodic_task(
        'pg-rotate-tasks-history-periodic',
    )

    generated_tasks = get_logged_tasks(pgsql)
    assert generated_tasks == 10

    mocked_time.sleep(3600 * 25)

    generated_tasks = get_logged_tasks(pgsql)
    assert generated_tasks == 10

    await taxi_crm_scheduler.run_periodic_task(
        'pg-rotate-tasks-history-periodic',
    )

    generated_tasks = get_logged_tasks(pgsql)
    assert generated_tasks == 0

    old_tasks = get_logged_tasks_old(pgsql)
    assert old_tasks == 10

    mocked_time.sleep(3600 * 25)

    await taxi_crm_scheduler.run_periodic_task(
        'pg-rotate-tasks-history-periodic',
    )

    old_tasks = get_logged_tasks_old(pgsql)
    assert old_tasks == 0

    generated_tasks = get_logged_tasks(pgsql)
    assert generated_tasks == 0


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_force_stopped_modified(taxi_crm_scheduler, pgsql, mocked_time):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.post('/v1/get_task_list', {})

    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1000, 350),
    )
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1001, 350),
    )
    payload_error = {
        'task_id': 1002,
        'new_state': 'error',
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
        'error_string': 'First Error',
    }
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload_error)

    payload_error = {
        'task_id': 1003,
        'new_state': 'error',
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
        'error_string': 'Second Error',
    }
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload_error)

    # generated send tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    # cleanup last step
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.post('/v1/get_task_list', {})  # policy
    await taxi_crm_scheduler.post('/v1/get_task_list', {})  # logs
    await taxi_crm_scheduler.post('/v1/get_task_list', {})  # push

    await taxi_crm_scheduler.post(
        '/v1/stop_sending',
        {'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003'},
    )

    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1031, 200),
    )

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.run_periodic_task(
        'pg-cleanup-stopped-sendings-periodic',
    )

    pg_finished = select_columns_from_table(
        'crm_scheduler.sendings_finished',
        ['sending_id', 'error', 'successfull'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert pg_finished == []

    mocked_time.sleep(100500)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 20):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    mocked_time.sleep(100500)
    payload = {
        'task_id': 1031,
        'new_state': 'ok',
        'logs_saved': 10,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }

    await taxi_crm_scheduler.run_periodic_task(
        'pg-cleanup-stopped-sendings-periodic',
    )

    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.run_periodic_task(
        'pg-cleanup-stopped-sendings-periodic',
    )

    pg_finished = select_columns_from_table(
        'crm_scheduler.sendings_finished',
        ['sending_id', 'error', 'successfull'],
        pgsql['crm_scheduler'],
        1000,
    )

    assert pg_finished == [
        {
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'error': (
                'Policy errors: ["First Error","Second Error"]. '
                'Send errors: []. Log errors: []. '
            ),
            'successfull': False,
        },
    ]
