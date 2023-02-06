# pylint: disable=import-only-modules
import datetime

import dateutil.parser
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table


CAMPAIGN1_ID, GROUP1_ID = 123, 456
CAMPAIGN2_ID, GROUP2_ID = 987, 654


def admin_get_meta_list_response():
    return {
        'campaigns': [
            {
                'campaign_id': CAMPAIGN1_ID,
                'groups': [
                    {
                        'group_id': GROUP1_ID,
                        'allowed_time_scope': {
                            'start_scope_time': '2021-12-14T10:00:00Z',
                            'end_scope_time': '2022-12-10T10:00:00Z',
                            'start_time_sec': 28800,
                            'stop_time_sec': 64800,
                        },
                    },
                ],
            },
            {
                'campaign_id': CAMPAIGN2_ID,
                'groups': [
                    {
                        'group_id': GROUP2_ID,
                        'allowed_time_scope': {
                            'start_scope_time': '2021-10-01T12:00:00Z',
                            'end_scope_time': '2021-10-31T15:00:00Z',
                            'start_time_sec': 10 * 60 * 60,
                            'stop_time_sec': 18 * 60 * 60,
                        },
                    },
                ],
            },
        ],
        'actual_ts': '2021-12-14T14:00:00Z',
    }


EXPECTED_SENDINGS = {
    (CAMPAIGN1_ID, GROUP1_ID): [
        {
            'work_date_start': datetime.datetime(2021, 12, 14, 10, 0),
            'work_date_finish': datetime.datetime(2022, 12, 10, 10, 0),
            'work_time_start': 8 * 60 * 60,
            'work_time_finish': 18 * 60 * 60,
        },
    ],
    (CAMPAIGN2_ID, GROUP2_ID): [
        {
            'work_date_start': datetime.datetime(2021, 10, 1, 12, 0),
            'work_date_finish': datetime.datetime(2021, 10, 31, 15, 0),
            'work_time_start': 10 * 60 * 60,
            'work_time_finish': 18 * 60 * 60,
        },
    ],
}


def generate_payload(task_id, allowed, logs_saved=0):
    return {
        'task_id': task_id,
        'new_state': 'ok',
        'filter_approved': allowed,
        'logs_saved': logs_saved,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }


async def get_task_list(taxi_crm_scheduler, number_of_calls=20):
    all_tasks = []
    for _ in range(number_of_calls):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})
        response_json = response.json()
        if response_json['task_type'] != 'idle':
            tasks = response_json['task_list']
            all_tasks += tasks
    return all_tasks


@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
@pytest.mark.parametrize('full_update', [False, True])
async def test_crm_admin_campaigns_meta_saved(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        full_update,
        crm_admin_get_list_mock,
):
    await taxi_crm_scheduler.invalidate_caches(clean_update=full_update)

    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'work_date_start',
            'work_date_finish',
            'work_time_start',
            'work_time_finish',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == EXPECTED_SENDINGS[(CAMPAIGN1_ID, GROUP1_ID)]


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': False,
    },
)
@pytest.mark.parametrize(
    ('success', 'now', 'campaign_id', 'group_id'),
    [
        pytest.param(
            True,
            dateutil.parser.parse('2020-04-21T12:17:42+00:00'),
            CAMPAIGN1_ID,
            GROUP1_ID,
            id='communication_will_be_actual',
        ),
        pytest.param(
            True,
            dateutil.parser.parse('2021-12-31T11:00+00:00'),
            CAMPAIGN1_ID,
            GROUP1_ID,
            id='communication_is_actual',
        ),
        pytest.param(
            False,
            dateutil.parser.parse('2022-12-31T11:00+00:00'),
            CAMPAIGN1_ID,
            GROUP1_ID,
            id='communication_has_expired_A',
        ),
        pytest.param(
            False,
            dateutil.parser.parse('2021-10-31T15:01:42+00:00'),
            CAMPAIGN2_ID,
            GROUP2_ID,
            id='communication_has_expired_B',
        ),
        pytest.param(
            True,
            dateutil.parser.parse('2021-10-31T14:29:42+00:00'),
            CAMPAIGN2_ID,
            GROUP2_ID,
            id='communication_is_valid_B',
        ),
    ],
)
async def test_crm_admin_check_work_time_on_registry_api1(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        success,
        now,
        group_id,
        campaign_id,
        crm_admin_get_list_mock,
):
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=True)

    response = await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': campaign_id,
            'channel_type': 'driver_push',
            'group_id': group_id,
            'policy_enabled': True,
            'send_enabled': True,
            'company_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
        },
    )

    if not success:
        assert response.status == 400
        return

    assert response.status == 200

    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'work_date_start',
            'work_date_finish',
            'work_time_start',
            'work_time_finish',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == EXPECTED_SENDINGS[(campaign_id, group_id)]


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': False,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.parametrize(
    ('success', 'now', 'campaign_id', 'group_id'),
    [
        pytest.param(
            True,
            dateutil.parser.parse('2020-04-21T12:17:42+00:00'),
            CAMPAIGN1_ID,
            GROUP1_ID,
            id='communication_will_be_actual',
        ),
        pytest.param(
            True,
            dateutil.parser.parse('2021-12-31T11:00+00:00'),
            CAMPAIGN1_ID,
            GROUP1_ID,
            id='communication_is_actual',
        ),
        pytest.param(
            False,
            dateutil.parser.parse('2022-12-31T11:00+00:00'),
            CAMPAIGN1_ID,
            GROUP1_ID,
            id='communication_has_expired_A',
        ),
        pytest.param(
            False,
            dateutil.parser.parse('2021-10-31T15:01:42+00:00'),
            CAMPAIGN2_ID,
            GROUP2_ID,
            id='communication_has_expired_B',
        ),
        pytest.param(
            True,
            dateutil.parser.parse('2021-10-31T14:29:42+00:00'),
            CAMPAIGN2_ID,
            GROUP2_ID,
            id='communication_is_valid_B',
        ),
    ],
)
async def test_crm_admin_check_work_time_on_registry_api2(
        taxi_crm_scheduler,
        mockserver,
        pgsql,
        mocked_time,
        success,
        now,
        group_id,
        campaign_id,
        crm_admin_get_list_mock,
):
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=True)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': str(campaign_id),
            'group_id': str(group_id),
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_push',
            'steps': ['crm_policy', 'eda_push', 'driver_push', 'logs'],
        },
    )
    if not success:
        assert response.status == 400
        return

    assert response.status == 200
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'work_date_start',
            'work_date_finish',
            'work_time_start',
            'work_time_finish',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == EXPECTED_SENDINGS[(campaign_id, group_id)]


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
    },
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': False,
        'check_work_time_on_generation': True,
    },
)
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign.sql',
    ],
)
async def test_generation_working_time(taxi_crm_scheduler, pgsql, mocked_time):
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    # Checking twice a row execution was fixed.
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    generated_task_sending_finished = select_columns_from_table(
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

    generated_task_logs_count = read_count(pgsql, 'task_pool_logs')

    # 13 chunks, 12 in size of 1000 and one in size of 300
    assert generated_task_logs_count == 13

    assert generated_task_sending_finished == [
        {
            'id': 1013,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': False,
            'error': 'Sending has expired',
            'error_details': ['Policy error: working time has expired'],
            'task_received': False,
        },
    ]

    for _ in range(4):
        response = await taxi_crm_scheduler.post('/v1/get_task_list', {})

    assert response.json() == {
        'task_type': 'sending_finished',
        'task_list': [],
        'sending_finished_info': {
            'id': 1013,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': False,
            'error': 'Sending has expired',
            'error_detail': ['Policy error: working time has expired'],
        },
    }

    for task_id in range(1000, 1013):
        payload = {
            'task_id': task_id,
            'new_state': 'ok',
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
        }
        response = await taxi_crm_scheduler.post(
            '/v1/report_task_ended', payload,
        )

    # cleanup log task
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    for task_id in range(1013, 1014):
        payload = {
            'task_id': task_id,
            'new_state': 'ok',
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
        }
        response = await taxi_crm_scheduler.post(
            '/v1/report_task_ended', payload,
        )

    finished_sendings = select_columns_from_table(
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

    assert finished_sendings == [
        {
            'id': 1,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': str(CAMPAIGN1_ID),
            'size': 12300,
            'policy_enabled': True,
            'send_enabled': True,
            'successfull': False,
            'error': 'Sending has expired',
            'error_details': ['Policy error: working time has expired'],
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


@pytest.mark.config(
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 120,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': False,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_TASKS_QUOTA_V6={
        'counter_filter': {
            'access_thread_count': 1,
            'bulk_size': 1000,
            'estimated_process_speed_per_sec': 1000,
        },
        'crm_policy': {
            'access_thread_count': 1,
            'bulk_size': 400,
            'estimated_process_speed_per_sec': 10,
        },
        'driver_push': {
            'access_thread_count': 1,
            'bulk_size': 250,
            'estimated_process_speed_per_sec': 250,
        },
        'driver_sms': {
            'access_thread_count': 1,
            'bulk_size': 10,
            'estimated_process_speed_per_sec': 10,
        },
        'driver_wall': {
            'access_thread_count': 1,
            'bulk_size': 1000,
            'estimated_process_speed_per_sec': 1000,
        },
        'eda_push': {
            'access_thread_count': 1,
            'bulk_size': 400,
            'estimated_process_speed_per_sec': 400,
        },
        'logs': {
            'access_thread_count': 1,
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
            'access_thread_count': 1,
            'bulk_size': 25,
            'estimated_process_speed_per_sec': 25,
        },
        'user_push': {
            'access_thread_count': 1,
            'bulk_size': 200,
            'estimated_process_speed_per_sec': 200,
        },
        'user_tags': {
            'access_thread_count': 1,
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
@pytest.mark.suspend_periodic_tasks('task-generator-periodic')
@pytest.mark.pgsql(
    'crm_scheduler',
    files=[
        'drop_sequence.sql',
        'create_channels_and_priorities_default.sql',
        'register_campaign_v2.sql',
    ],
)
async def test_generation_working_time_v2_expired(
        taxi_crm_scheduler, pgsql, mocked_time,
):
    now = datetime.datetime(2021, 12, 2, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=False)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    generated_task_policy_count = read_count(pgsql, 'task_pool_crm_policy')
    assert generated_task_policy_count == 2

    assert (
        len(await get_task_list(taxi_crm_scheduler))
        == generated_task_policy_count
    )

    for task_id in range(1000, 1002):
        payload = generate_payload(task_id, 400)
        response = await taxi_crm_scheduler.post(
            '/v2/report_task_ended', payload,
        )
        assert response.status == 200

    # Set time to the future when sending will be expired
    now = datetime.datetime(2022, 1, 1, 11, 0)
    mocked_time.set(now)

    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    assert read_count(pgsql, 'task_pool_crm_policy') == 0
    assert read_count(pgsql, 'task_pool_counter_filter') == 1
    assert read_count(pgsql, 'task_pool_logs') == 2

    all_tasks = await get_task_list(taxi_crm_scheduler)

    expired_logs_tasks = [task for task in all_tasks if task['step_num'] == 5]
    policy_tasks = [task for task in all_tasks if task['step_num'] == 1]
    second_step_tasks = [task for task in all_tasks if task['step_num'] == 2]

    assert expired_logs_tasks == [
        {
            'id': 1002,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'time_delay_ms': 10000,
            'task_properties': [
                {'scope_start': 801, 'scope_end': 10800, 'expired': True},
            ],
            'step_num': 5,
            'task_ids_to_log': [],
        },
        {
            'id': 1003,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'time_delay_ms': 10000,
            'task_properties': [
                {'scope_start': 10801, 'scope_end': 12300, 'expired': True},
            ],
            'step_num': 5,
            'task_ids_to_log': [],
        },
    ]
    assert not policy_tasks
    assert second_step_tasks == [
        {
            'id': 1004,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'time_delay_ms': 1000,
            'task_properties': [
                {'offset': 0, 'size': 400, 'source_task_id': 1000},
                {'offset': 0, 'size': 400, 'source_task_id': 1001},
            ],
            'step_num': 2,
        },
    ]

    gen_sending_finished_count = read_count(
        pgsql, 'task_pool_sending_finished',
    )
    assert gen_sending_finished_count == 0

    payload = generate_payload(1004, 800)

    response = await taxi_crm_scheduler.post('/v2/report_task_ended', payload)
    assert response.status == 200

    for task_id, logs_saved in ((1002, 10000), (1003, 1500)):
        payload = generate_payload(task_id, 0, logs_saved)
        response = await taxi_crm_scheduler.post(
            '/v2/report_task_ended', payload,
        )
        assert response.status == 200

    for step, task_id in ((3, 1005), (4, 1006), (5, 1007)):
        mocked_time.sleep(300)
        await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

        all_tasks = await get_task_list(taxi_crm_scheduler)

        current_step_tasks = [
            task for task in all_tasks if task['step_num'] == step
        ]
        another_tasks = [
            task for task in all_tasks if task['step_num'] != step
        ]

        assert another_tasks == []
        assert len(current_step_tasks) == 1

        payload = {}
        if step < 5:
            payload = generate_payload(task_id, 800)
        else:
            payload = generate_payload(task_id, 0, 800)

        response = await taxi_crm_scheduler.post(
            '/v2/report_task_ended', payload,
        )
        assert response.status == 200

    # Need two tick of generation here
    mocked_time.sleep(300)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    mocked_time.sleep(300)
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')

    generated_task_sending_finished = select_columns_from_table(
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

    assert generated_task_sending_finished == [
        {
            'id': 1008,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': False,
            'error': 'Sending has expired',
            'error_details': [
                'Send to channel error: working time has expired',
            ],
            'task_received': False,
        },
    ]

    all_responses = []
    for _ in range(20):
        response = await taxi_crm_scheduler.post('/v2/get_task_list', {})
        response_json = response.json()
        if response_json['task_type'] != 'idle':
            all_responses.append(response.json())

    assert len(all_responses) == 1
    sending_finished_task = all_responses[0]

    assert sending_finished_task == {
        'task_type': 'sending_finished',
        'task_list': [],
        'sending_finished_info': {
            'id': 1008,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'successfull': False,
            'error': 'Sending has expired',
            'error_detail': [
                'Send to channel error: working time has expired',
            ],
        },
    }

    payload = generate_payload(1008, 0)
    response = await taxi_crm_scheduler.post('/v1/report_task_ended', payload)
    assert response.status == 200

    gen_sending_finished_count = read_count(
        pgsql, 'task_pool_sending_finished',
    )
    assert gen_sending_finished_count == 0

    sendings_count = read_count(pgsql, 'sendings')
    assert sendings_count == 0

    sendings_runtime_count = read_count(pgsql, 'sendings_runtime')
    assert sendings_runtime_count == 0
