# pylint: disable=import-only-modules
import pytest

from tests_crm_scheduler.utils import read_count


def generate_payload(task_id, allowed):
    return {
        'task_id': task_id,
        'new_state': 'ok',
        'filter_approved': allowed,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


async def report_compleated_task(
        taxi_crm_scheduler, task_id, num_filter_allowed,
):
    payload = generate_payload(task_id, num_filter_allowed)
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
        'add_sending.sql',
    ],
)
async def test_whole_v2_api(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_crm_policy') == 4

    for _ in range(1, 2):
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

    await report_compleated_task(taxi_crm_scheduler, 1000, 350)
    await report_compleated_task(taxi_crm_scheduler, 1001, 350)
    await report_compleated_task(taxi_crm_scheduler, 1002, 350)
    await report_compleated_task(taxi_crm_scheduler, 1003, 350)

    mocked_time.sleep(100500)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_counter_filter') == 2
    assert read_count(pgsql, 'task_pool_logs') == 1

    for _ in range(1, 14):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'filter_step',
        'task_list': [
            {
                'id': 1005,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 0, 'size': 350, 'source_task_id': 1000},
                    {'offset': 0, 'size': 350, 'source_task_id': 1001},
                    {'offset': 0, 'size': 300, 'source_task_id': 1002},
                ],
                'step_num': 2,
            },
            {
                'id': 1006,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 300, 'size': 50, 'source_task_id': 1002},
                    {'offset': 0, 'size': 350, 'source_task_id': 1003},
                ],
                'step_num': 2,
            },
        ],
    }

    assert read_count(pgsql, 'task_pool_counter_filter_in_process') == 2
    assert read_count(pgsql, 'task_pool_logs_in_process') == 1

    await report_compleated_task(taxi_crm_scheduler, 1005, 732)
    await report_compleated_task(taxi_crm_scheduler, 1006, 378)
    await report_compleated_task(taxi_crm_scheduler, 1004, 123)

    mocked_time.sleep(100500)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 14):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'pipe_step',
        'task_list': [
            {
                'id': 1008,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 0, 'size': 732, 'source_task_id': 1005},
                    {'offset': 0, 'size': 268, 'source_task_id': 1006},
                ],
                'step_num': 3,
            },
            {
                'id': 1009,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 268, 'size': 110, 'source_task_id': 1006},
                ],
                'step_num': 3,
            },
        ],
    }

    await report_compleated_task(taxi_crm_scheduler, 1007, 123)
    await report_compleated_task(taxi_crm_scheduler, 1008, 1000)
    await report_compleated_task(taxi_crm_scheduler, 1009, 110)

    mocked_time.sleep(100500)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    for _ in range(1, 7):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'pipe_step',
        'task_list': [
            {
                'id': 1010,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 0, 'size': 1000, 'source_task_id': 1008},
                ],
                'step_num': 4,
            },
            {
                'id': 1011,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 0, 'size': 110, 'source_task_id': 1009},
                ],
                'step_num': 4,
            },
        ],
    }

    await report_compleated_task(taxi_crm_scheduler, 1010, 1000)
    await report_compleated_task(taxi_crm_scheduler, 1011, 110)

    mocked_time.sleep(100500)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 13):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    assert response.json() == {
        'task_type': 'pipe_step',
        'task_list': [
            {
                'id': 1012,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 0, 'size': 1000, 'source_task_id': 1010},
                ],
                'step_num': 5,
                'task_ids_to_log': [],
            },
            {
                'id': 1013,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [
                    {'offset': 0, 'size': 110, 'source_task_id': 1011},
                ],
                'step_num': 5,
                'task_ids_to_log': [],
            },
        ],
    }

    await report_compleated_task(taxi_crm_scheduler, 1012, 1000)
    await report_compleated_task(taxi_crm_scheduler, 1013, 110)

    assert read_count(pgsql, 'task_reported_default') == 4
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 20):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})

    await report_compleated_task(taxi_crm_scheduler, 1014, 0)
    assert read_count(pgsql, 'sendings_finished') == 1
