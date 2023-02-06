# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count


def generate_payload(task_id, allowed, logs_saved=0):
    return {
        'task_id': task_id,
        'new_state': 'ok',
        'policy_allowed': allowed,
        'logs_saved': logs_saved,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 4,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 10,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
        'drop_sequence.sql',
    ],
)
async def test_policy_generated_freely(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    # check that policy generated freely
    # before has send task generated
    # or policy finished some tasks
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    policy_before = read_count(pgsql, 'task_pool_crm_policy')
    assert policy_before == 10
    await taxi_crm_scheduler.post('/v1/get_task_list', {})
    await taxi_crm_scheduler.post('/v1/get_task_list', {})

    policy_after = read_count(pgsql, 'task_pool_crm_policy')
    assert policy_after == 2
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    policy_after_generated = read_count(pgsql, 'task_pool_crm_policy')
    assert policy_after_generated == 10


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 4,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 10,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
        'drop_sequence.sql',
    ],
)
async def test_policy_blocked_by_reported(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.post('/v1/get_task_list', {})
    await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1000, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1001, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1002, 1)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1003, 1)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    mocked_time.sleep(15)

    policy_tasks_count = read_count(pgsql, 'task_pool_crm_policy')
    assert policy_tasks_count == 2

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # check that we not generated new tasks
    # due to policy reported tasks
    policy_tasks_count = read_count(pgsql, 'task_pool_crm_policy')
    assert policy_tasks_count == 2


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 4,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 10,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
        'drop_sequence.sql',
    ],
)
async def test_policy_blocked_by_send_task(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.post('/v1/get_task_list', {})
    await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1000, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1001, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1002, 150)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1003, 150)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_payload(1004, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1005, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1006, 150)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1007, 150)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    assert read_count(pgsql, 'task_pool_crm_policy') == 2
    mocked_time.sleep(15)
    # generate send tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_user_push') == 2
    assert read_count(pgsql, 'task_pool_crm_policy') == 2
    # skip time to send task block policy generation
    mocked_time.sleep(15)

    # clean up used reported tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_user_push') == 2
    assert read_count(pgsql, 'task_pool_crm_policy') == 2
    # nothing changing
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_user_push') == 2
    assert read_count(pgsql, 'task_pool_crm_policy') == 2

    # recieve tasks
    for _ in range(1, 20):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    # now policy must be allowed to generate tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_crm_policy') == 10


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 4,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 1,
        'policy_allowance_in_seconds': 10,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
        'drop_sequence.sql',
    ],
)
async def test_policy_blocked_by_send_task_v2(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.post('/v1/get_task_list', {})
    await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1000, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1001, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1002, 150)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1003, 150)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_payload(1004, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1005, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1006, 150)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1007, 150)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    assert read_count(pgsql, 'task_pool_crm_policy') == 2
    mocked_time.sleep(15)
    # generate send tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_user_push') == 2
    assert read_count(pgsql, 'task_pool_crm_policy') == 2
    # skip time to send task block policy generation
    mocked_time.sleep(15)

    # clean up used reported tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_user_push') == 2
    assert read_count(pgsql, 'task_pool_crm_policy') == 2
    # nothing changing
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_user_push') == 2
    assert read_count(pgsql, 'task_pool_crm_policy') == 2

    # recieve tasks
    for _ in range(1, 20):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    # now policy must be allowed to generate tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_crm_policy') == 10
