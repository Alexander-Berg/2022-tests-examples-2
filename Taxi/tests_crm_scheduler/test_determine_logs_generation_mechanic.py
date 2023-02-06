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


def generate_log_v2_payload(task_id, logs_saved):
    return {
        'task_id': task_id,
        'logs_saved': logs_saved,
        'new_state': 'ok',
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_register_sending_v1(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 12300,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            # 'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            # 'group_id': '0_testing',
            'channel_type': 'user_push',
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
        },
    )
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        ['generation_version'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == [{'generation_version': 2}]


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 2,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
async def test_register_sending_v2(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock,
):
    await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 12300,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': '123',
            'group_id': '456',
            # 'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            # 'group_id': '0_testing',
            'channel_type': 'user_push',
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
        },
    )
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        ['generation_version'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == [{'generation_version': 2}]


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 2,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
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
async def test_v2_generation(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1000, 139)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    # check logs empty
    assert read_count(pgsql, 'task_pool_logs') == 0

    mocked_time.sleep(300)
    # check logs still empty
    assert read_count(pgsql, 'task_pool_logs') == 0

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # check logs generate task on policy disallowed messages
    assert read_count(pgsql, 'task_pool_logs') == 1

    # check log v2 task recieved
    for _ in range(1, 3):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
    assert response.json() == {
        'task_type': 'send_to_log',
        'task_list': [
            {
                'id': 1010,
                'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
                'time_delay_ms': 1000,
                'task_properties': [],
                'task_ids_to_log': [1000],
            },
        ],
    }

    # proceed to get send to channel task
    for _ in range(1, 6):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1011, 139)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    mocked_time.sleep(300)

    reported_tasks = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['id, logs_generated '],
        pgsql['crm_scheduler'],
        1000,
    )
    assert reported_tasks == [
        {'id': 1000, 'logs_generated': True},
        {'id': 1011, 'logs_generated': False},
    ]

    # check it clean already processed reported task +
    # generate new log task for finished send task
    # here we also got restarted due timeout old log task
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_logs') == 2

    reported_tasks = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['id, logs_generated '],
        pgsql['crm_scheduler'],
        1000,
    )
    assert reported_tasks == [{'id': 1011, 'logs_generated': True}]

    # check that log task restarted correctly
    logs_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_logs',
        ['id, retry_count, task_ids_to_log'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert logs_tasks == [
        {'id': 1010, 'retry_count': 1, 'task_ids_to_log': [1000]},
        {'id': 1012, 'retry_count': 0, 'task_ids_to_log': [1011]},
    ]

    # proceed to get log tasks
    for _ in range(1, 10):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1001, 1)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1002, 2)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1003, 3)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1004, 4)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_log_v2_payload(1010, 100)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_log_v2_payload(1012, 100)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    # test cleanup processed send task,
    # and generate new log task from 3 send policy tasks
    assert read_count(pgsql, 'task_reported_default') == 7
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_reported_default') == 4
    assert read_count(pgsql, 'task_pool_logs') == 1
    logs_tasks = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['id, logs_generated'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert logs_tasks == [
        {'id': 1004, 'logs_generated': False},
        {'id': 1001, 'logs_generated': True},
        {'id': 1002, 'logs_generated': True},
        {'id': 1003, 'logs_generated': True},
    ]

    # try to get to finish sending
    # proceed to get all tasks
    for _ in range(1, 60):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1005, 300)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1006, 350)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1007, 370)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1008, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    mocked_time.sleep(300)
    for _ in range(1, 60):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 60):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1009, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_log_v2_payload(1013, 100)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_log_v2_payload(1014, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_payload(1015, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    mocked_time.sleep(300)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 60):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_payload(1016, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1018, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    payload = generate_log_v2_payload(1017, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    mocked_time.sleep(300)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 60):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_log_v2_payload(1019, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(1, 60):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    payload = generate_log_v2_payload(1020, 390)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    assert read_count(pgsql, 'sendings') == 0
    assert read_count(pgsql, 'sendings_finished') == 1


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 2,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'create_channels_and_priorities_default.sql',
        'register_testing_campaign.sql',
        'drop_sequence.sql',
    ],
)
async def test_v2_logging_disabled_for_test_sendings(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    assert read_count(pgsql, 'task_pool_sending_finished') == 0

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_sending_finished') == 1


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 2,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'create_channels_and_priorities_default.sql',
        'register_testing_campaign_2.sql',
        'drop_sequence.sql',
    ],
)
async def test_v2_generation_test_sending(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for _ in range(10):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
        assert response.status == 200

    payload = generate_payload(1000, 1)
    res = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    assert res.status == 200
    payload = generate_payload(1001, 1)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    assert res.status == 200

    mocked_time.sleep(5000)

    for _ in range(20):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
        assert response.status == 200

    payload = generate_payload(1002, 3)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    payload = generate_payload(1003, 4)
    await taxi_crm_scheduler.post('/v1/report_task_ended', payload)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    # check logs empty
    assert read_count(pgsql, 'task_pool_logs') == 0

    mocked_time.sleep(300)
    # check logs still empty
    assert read_count(pgsql, 'task_pool_logs') == 0

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # check logs generate task on policy disallowed messages
    assert read_count(pgsql, 'task_pool_logs') == 0

    assert read_count(pgsql, 'task_pool_sending_finished') != 0

    # proceed to get send to channel task
    for _ in range(1, 8):
        await taxi_crm_scheduler.post('/v1/get_task_list', {})

    mocked_time.sleep(300)

    reported_tasks = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['id, logs_generated '],
        pgsql['crm_scheduler'],
        1000,
    )
    assert reported_tasks == [
        {'id': 1000, 'logs_generated': False},
        {'id': 1001, 'logs_generated': False},
        {'id': 1002, 'logs_generated': False},
        {'id': 1003, 'logs_generated': False},
    ]

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    assert read_count(pgsql, 'task_pool_logs') == 0

    logs_tasks = select_columns_from_table(
        'crm_scheduler.task_pool_logs',
        ['id, retry_count, task_ids_to_log'],
        pgsql['crm_scheduler'],
        1000,
    )
    assert logs_tasks == []

    for _ in range(1, 10):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})
        assert response.status == 200

    payload = generate_payload(1004, 0)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    assert response.status == 200

    mocked_time.sleep(300)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    reported_tasks = select_columns_from_table(
        'crm_scheduler.task_reported_default',
        ['id, logs_generated '],
        pgsql['crm_scheduler'],
        1000,
    )
    assert reported_tasks == []

    assert read_count(pgsql, 'sendings') == 0
    assert read_count(pgsql, 'sendings_finished') == 1


@pytest.mark.suspend_periodic_tasks('pg-cleanup-stopped-sendings-periodic')
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 5,
        'workers_period_in_seconds': 2,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
    },
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': False,
        'check_work_time_on_generation': True,
    },
    # Only one important field here!
    #
    # We set 'crm_policy' bulk_size to zero to force
    # generation pass over logs task before policy tasks was
    # generated
    CRM_SCHEDULER_TASKS_QUOTA_V6={
        'counter_filter': {
            'access_thread_count': 1,
            'bulk_size': 1000,
            'estimated_process_speed_per_sec': 1000,
        },
        'crm_policy': {
            'access_thread_count': 4,
            # This is the only one important field here!
            'bulk_size': 0,
            'estimated_process_speed_per_sec': 400,
        },
        'driver_push': {
            'access_thread_count': 4,
            'bulk_size': 250,
            'estimated_process_speed_per_sec': 250,
        },
        'driver_sms': {
            'access_thread_count': 10,
            'bulk_size': 10,
            'estimated_process_speed_per_sec': 10,
        },
        'driver_wall': {
            'access_thread_count': 1,
            'bulk_size': 400,
            'estimated_process_speed_per_sec': 400,
        },
        'eda_push': {
            'access_thread_count': 20,
            'bulk_size': 400,
            'estimated_process_speed_per_sec': 400,
        },
        'logs': {
            'access_thread_count': 5,
            'bulk_size': 10000,
            'estimated_process_speed_per_sec': 1000,
        },
        'promo': {
            'access_thread_count': 1,
            'bulk_size': 1000,
            'estimated_process_speed_per_sec': 1000,
        },
        'sending_finished': {
            'access_thread_count': 1,
            'bulk_size': 1,
            'estimated_process_speed_per_sec': 1,
        },
        'user_eda_sms': {
            'access_thread_count': 4,
            'bulk_size': 25,
            'estimated_process_speed_per_sec': 25,
        },
        'user_push': {
            'access_thread_count': 5,
            'bulk_size': 200,
            'estimated_process_speed_per_sec': 200,
        },
        'user_tags': {
            'access_thread_count': 5,
            'bulk_size': 20000,
            'estimated_process_speed_per_sec': 20000,
        },
        'z_user_push': {
            'access_thread_count': 1,
            'bulk_size': 1000,
            'estimated_process_speed_per_sec': 1000,
        },
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
# Test for reproducing bug
# https://st.yandex-team.ru/TAXICRMDEV-1914
async def test_no_expired_logs_generation_race_fix(
        taxi_crm_scheduler, mockserver, pgsql, mocked_time,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    # check logs empty
    assert read_count(pgsql, 'task_pool_logs') == 0
