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


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_force_stop_sending(taxi_crm_scheduler, pgsql):
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
        '/v1/report_task_ended', generate_payload(1003, 200),
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
        '/v1/stop_sending',
        {'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003'},
    )

    response = await taxi_crm_scheduler.post(
        '/v1/report_task_ended', generate_payload(1031, 200),
    )

    # check non tasks be generated
    for _ in range(1, 20):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
        assert response.json() == {'task_type': 'idle', 'task_list': []}

    assert read_count(pgsql, 'task_reported_default') == 1

    assert read_count(pgsql, 'task_pool_crm_policy_in_process') == 0

    assert read_count(pgsql, 'task_pool_user_push_in_process') == 0

    assert read_count(pgsql, 'task_pool_crm_policy') == 0

    assert read_count(pgsql, 'task_pool_user_push') == 0


@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_force_stop_sending_failed(taxi_crm_scheduler, pgsql):
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
        '/v1/report_task_ended', generate_payload(1003, 200),
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
        '/v1/stop_sending',
        {'sending_id': '7d27b35a-0032-11ec-9a03-0142ac130003'},
    )

    assert response.json() == {
        'message': (
            'Can\'t force stop sending, '
            'no such sending_id: 7d27b35a-0032-11ec-9a03-0142ac130003'
        ),
        'code': '400',
    }
