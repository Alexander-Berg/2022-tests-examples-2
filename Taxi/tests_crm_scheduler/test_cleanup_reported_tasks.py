# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table


def generate_payload(task_id, allowed):
    return {
        'task_id': task_id,
        'new_state': 'ok',
        'policy_allowed': allowed,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_cleanup_tasks(taxi_crm_scheduler, pgsql, mocked_time):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    # Check if all policy tasks generated
    assert read_count(pgsql, 'task_pool_crm_policy_in_process') == 10

    response = await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1000, 350),
    )
    response = await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1001, 350),
    )
    response = await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1002, 300),
    )
    response = await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1003, 180),
    )

    # generated send tasks
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 4

    # cleanup last step
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 4

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
                        'size': 350,
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
                        'size': 300,
                    },
                ],
            },
        ],
    }

    response = await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1031, 200),
    )

    assert read_count(pgsql, 'task_reported_default') == 5

    # generate log task
    mocked_time.sleep(300)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 0

    # generate cleanup push task
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_reported_default') == 0

    for _ in range(1, 10):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
    assert response.json() == {
        'task_type': 'send_to_log',
        'task_list': [
            {
                'id': 1032,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [],
                'task_ids_to_log': [1003, 1000, 1001, 1002, 1031],
            },
        ],
    }
    response = await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1032, 200),
    )
    assert read_count(pgsql, 'task_reported_default') == 1

    # cleanup log task
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_reported_default') == 0


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_cleanup_retry_failed_tasks(taxi_crm_scheduler, pgsql, load):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    await taxi_crm_scheduler.post('/v1/get_task_list', {})

    pgsql['crm_scheduler'].cursor().execute(
        load('make_retry_failed_policy_tasks.sql'),
    )

    # Check if all policy tasks generated

    assert read_count(pgsql, 'task_pool_crm_policy_in_process') == 11
    failed_count = select_columns_from_table(
        'crm_scheduler.sendings_runtime',
        ['policy_summ_failed'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert failed_count == [{'policy_summ_failed': 0}]

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_crm_policy_in_process') == 10

    failed_count = select_columns_from_table(
        'crm_scheduler.sendings_runtime',
        ['policy_summ_failed'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert failed_count == [{'policy_summ_failed': 400}]
