# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count


def generate_payload(task_id, allowed):
    return {
        'task_id': task_id,
        'new_state': 'ok',
        'policy_allowed': allowed,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_big_campaign.sql',
        'add_all_tasks.sql',
    ],
)
async def test_soft_stop_sending(taxi_crm_scheduler, pgsql, mocked_time):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)

    assert read_count(pgsql, 'task_pool_crm_policy') == 1
    assert read_count(pgsql, 'task_pool_crm_policy_in_process') == 1
    assert read_count(pgsql, 'task_pool_user_push') == 1
    assert read_count(pgsql, 'task_pool_user_push_in_process') == 1
    assert read_count(pgsql, 'task_pool_logs') == 1
    assert read_count(pgsql, 'task_pool_logs_in_process') == 1
    assert read_count(pgsql, 'task_reported_default') == 2

    # Now we have tasks
    # crm_policy - 1 in pool 1 in process 1 reported
    # user_push - 1 in pool 1 in process 1 reported
    # logs - 1 in pool 1 in process

    await taxi_crm_scheduler.post(
        '/v1/stop_sending',
        {'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003'},
    )

    # Now we MUST have tasks, clearing all that can be not logged
    # crm_policy - 0 in pool 0 in process 0 reported
    # user_push - 0 in pool 1 in process 1 reported
    # logs - 1 in pool 1 in process

    assert read_count(pgsql, 'task_pool_crm_policy') == 0
    assert read_count(pgsql, 'task_pool_crm_policy_in_process') == 0
    assert read_count(pgsql, 'task_pool_user_push') == 0
    assert read_count(pgsql, 'task_pool_user_push_in_process') == 1
    assert read_count(pgsql, 'task_pool_logs') == 1
    assert read_count(pgsql, 'task_pool_logs_in_process') == 1
    assert read_count(pgsql, 'task_reported_default') == 1

    # check report send task is working
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(43, 350),
    )

    assert read_count(pgsql, 'task_reported_default') == 2

    # check generated tasks
    mocked_time.sleep(5000)

    # generate logs tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_logs') == 2

    # clean up
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_reported_default') == 0

    # finish pretest log task
    assert read_count(pgsql, 'task_pool_logs_in_process') == 1
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(12, 350),
    )
    assert read_count(pgsql, 'task_pool_logs_in_process') == 0

    # get generatedlog task in process
    for _ in range(1, 30):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert read_count(pgsql, 'task_pool_logs') == 0
    assert read_count(pgsql, 'task_pool_logs_in_process') == 2

    # finish first log task
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1002, 350),
    )

    # finish second log task
    await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1003, 350),
    )

    # cleanup logs reported tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    await taxi_crm_scheduler.run_periodic_task(
        'pg-cleanup-stopped-sendings-periodic',
    )
    assert read_count(pgsql, 'sendings_finished') == 1
