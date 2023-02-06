# pylint: disable=unused-variable,invalid-name,protected-access
from aiohttp import web
import pytest

from crm_hub.generated.custom_unit import run_cron
from crm_hub.logic import experiments_logger


def mock_policy(mockserver):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message_bulk')
    async def _policy_check(request):
        allowed = []
        for item in request.json['items']:
            allowed.append(bool(int(item['entity_id'][-1]) % 2))
        return mockserver.make_response(status=200, json={'allowed': allowed})


def mock_admin(mockserver, entity, channel_type, channel_name):
    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        return {
            'name': 'my_name',
            'entity_type': entity,
            'group_type': 'testing',
            'channel': channel_type,
            'yt_table': 'my_yt_table',
            'yt_test_table': 'my_yt_table_verification',
            'local_control': False,
            'global_control': False,
            'channel_info': {
                'channel_name': channel_name,
                'intent': 'none',
                'sender': 'sender',
                'text': 'text',
                'action': 'MessageNew',
                'content': 'my_content',
                'deeplink': 'my_deeplink',
                'code': 100,
                'ttl': 30,
                'collapse_key': 'MessageNew:test',
                'feed_id': 'id',
                'send_at': '2020-09-11T10:00:00+03:00',
                'type': 'type',
                'url': 'url',
                'title': 'title',
                'teaser': 'teaser',
            },
            'extra_data': {},
            'report_info': {
                'creation_day': 'friday_the_13th',
                'channel': channel_name,
                'experiment_name': 'experiment_name',
                'experiment_type': 'experiment_type',
                'experiment_id': 'experiment_id',
            },
        }


def mock_scheduler(
        sending_id,
        task_type,
        mockserver,
        properties,
        sending_successfull=None,
        task_items=None,
        task_id=1337,
):
    @mockserver.json_handler('/crm-scheduler/v1/report_task_ended')
    async def _notify_scheduler(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/crm-scheduler/v1/get_task_list')
    async def _action(request):
        meta_data = {
            'task_type': task_type,
            'task_list': (
                [
                    {
                        'id': task_id,
                        'time_delay_ms': 0,
                        'sending_id': sending_id,
                        'task_properties': properties,
                    },
                ]
                if not task_items
                else task_items
            ),
        }
        if sending_successfull is not None:
            meta_data['sending_finished_info'] = {
                'id': 0,
                'sending_id': sending_id,
                'successfull': sending_successfull,
                'error': 'some error message',
                'error_detail': [],
            }
        return mockserver.make_response(json=meta_data, status=200)


async def run_task(patch):
    @patch('crm_hub.daemon.daemon_runner.DaemonRunner._check_force_exit')
    async def _check_force_exit(*args, **kwargs):
        return True

    await run_cron.main(['crm_hub.daemon.run_daemon', '-t', '0'])


async def check_policy(
        passed_expected,
        filtered_expected,
        context,
        task_id,
        sending_table,
        control,
        logbroker_logs,
):
    async with context.pg.master_pool.acquire() as conn:
        policy_query = (
            f'SELECT count(*) FROM crm_hub.{sending_table} '
            'WHERE policy_allowed = {allowed} '
        )
        passed = await conn.fetchval(policy_query.format(allowed='TRUE'))
        filtered = await conn.fetchval(policy_query.format(allowed='FALSE'))

        assert passed == passed_expected
        assert filtered == filtered_expected

        logbroker_passed = 0
        logbroker_filtered = 0
        for log in logbroker_logs:
            if log['status'] == experiments_logger.ActionStatus.SUCCESS.value:
                logbroker_passed += 1
            if log['status'] == experiments_logger.ActionStatus.FILTERED.value:
                logbroker_filtered += 1

        has_task_id = await conn.fetchval(
            f'SELECT count(*) FROM crm_hub.{sending_table} '
            f'WHERE log_task_id = {task_id}',
        )
        if not control:
            assert has_task_id == filtered_expected
        else:
            assert has_task_id == filtered_expected + passed_expected


async def check_sending(sending_id, context, task_id, logbroker_chunks):
    query = 'SELECT * FROM crm_hub.sending_test_table ORDER BY id;'
    async with context.pg.master_pool.acquire() as conn:
        results = await conn.fetch(query)

    skips = successes = 0
    for inx, result in enumerate(results):
        if result['status'] == 'SKIP':
            assert 'policy' in result['reason']
            assert result['log_task_id'] is None
            skips += 1
        elif result['status'] == 'SUCCESS':
            assert result['log_task_id'] == 1337
            successes += 1
        else:
            raise ValueError(f'incorrect status for {inx}: {result["status"]}')

    logbroker_successes = set()
    logbroker_skips = set()
    logbroker_logs = [
        logbroker_log
        for logbroker_chunk in logbroker_chunks
        for logbroker_log in logbroker_chunk['data']
    ]
    for log in logbroker_logs:
        if log['status'] == experiments_logger.ActionStatus.SUCCESS.value:
            logbroker_successes.add(log['unique_entity_id'])
        if log['status'] == experiments_logger.ActionStatus.FILTERED.value:
            logbroker_skips.add(log['unique_entity_id'])

    assert skips == successes == 100
    assert len(logbroker_successes) == len(logbroker_skips) == 100


async def check_logging(
        context,
        yt_client,
        yt_table_path,
        verify,
        control,
        use_policy,
        pg_table=None,
        expired=False,
):

    if verify:
        return

    assert yt_client.get(yt_table_path + '/@row_count') == 200
    logs = yt_client.read_table(yt_table_path)
    sent = 100 if use_policy and not expired else 200

    if expired:
        assert sum(1 for _ in logs) == sent
    else:
        assert (
            sum(
                1
                for row in logs
                if row['properties']['communication_status'] == 'sent'
            )
            == sent
        )

    table_mapper = {
        (False, True): 'logging_test_table',
        (True, True): 'logging_control_table',
        (True, False): 'logging_control_wo_policy_table',
        (False, False): 'logging_test_wo_policy_table',
    }
    table = pg_table or table_mapper[(control, use_policy)]

    query = f'SELECT * FROM crm_hub.{table} ORDER BY id;'
    async with context.pg.master_pool.acquire() as conn:
        results = await conn.fetch(query)

    assert set(map(lambda r: r['was_logged'], results)) == {True}
    if expired:
        assert all(map(lambda r: r['status'] == 'EXPIRED', results))


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'policy_chunk_size': 100,
        'policy_max_connections': 4,
        'policy_use_results': True,
    },
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
    CRM_HUB_SCHEDULER={'deterministic_logs_enabled': True},
)
@pytest.mark.parametrize(
    'properties, passed, filtered, sending_id, sending_table, control',
    [
        (
            [{'scope_start': 1, 'scope_end': 200, 'size': 0, 'offset': 0}],
            100,
            100,
            '00000000000000000000000000000000',
            'policy_test_table',
            False,
        ),
        (
            [
                {'scope_start': 1, 'scope_end': 50, 'size': 0, 'offset': 0},
                {'scope_start': 51, 'scope_end': 100, 'size': 0, 'offset': 0},
                {'scope_start': 101, 'scope_end': 150, 'size': 0, 'offset': 0},
                {'scope_start': 151, 'scope_end': 200, 'size': 0, 'offset': 0},
            ],
            100,
            100,
            '00000000000000000000000000000000',
            'policy_test_table',
            False,
        ),
        (
            [{'scope_start': 1, 'scope_end': 200, 'size': 0, 'offset': 0}],
            100,
            100,
            '00000000000000000000000000000009',
            'policy_control_test_table',
            True,
        ),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
async def test_policy_check(
        cron_context,
        mockserver,
        patch,
        properties,
        passed,
        filtered,
        sending_id,
        sending_table,
        control,
):
    @patch('crm_hub.repositories.process_results.DataLoader.load_to_logbroker')
    async def load_to_logbroker(data, *args, **kwargs):
        pass

    task_id = 1337

    mock_scheduler(
        sending_id,
        'check_crm_policy',
        mockserver,
        properties,
        task_id=task_id,
    )
    mock_policy(mockserver)
    mock_admin(mockserver, 'Driver', 'SMS', 'driver_sms')

    await run_task(patch)
    await check_policy(
        passed,
        filtered,
        cron_context,
        task_id,
        sending_table,
        control,
        load_to_logbroker.calls[0]['data'],
    )


@pytest.mark.config(
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
    CRM_HUB_SCHEDULER={'deterministic_logs_enabled': True},
)
@pytest.mark.parametrize(
    'channel_type, entity, channel_name, properties',
    [
        (
            'SMS',
            'Driver',
            'driver_sms',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 100}],
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 25},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 25},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 25,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 25,
                },
            ],
        ),
        (
            'SMS',
            'User',
            'user_sms',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
        ),
        (
            'SMS',
            'User',
            'user_sms',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 50},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 50},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
        ),
        (
            'PUSH',
            'Driver',
            'driver_push',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
        ),
        (
            'PUSH',
            'Driver',
            'driver_push',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 50},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 50},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
        ),
        (
            'PUSH',
            'User',
            'user_push',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
        ),
        (
            'PUSH',
            'User',
            'user_push',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 50},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 50},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
        ),
        (
            'legacywall',
            'Driver',
            'driver_legacywall',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
        ),
        (
            'legacywall',
            'Driver',
            'driver_legacywall',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 50},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 50},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 20},
                {'scope_start': 1, 'scope_end': 50, 'offset': 20, 'size': 20},
                {'scope_start': 1, 'scope_end': 50, 'offset': 40, 'size': 10},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 25},
                {
                    'scope_start': 51,
                    'scope_end': 100,
                    'offset': 25,
                    'size': 25,
                },
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
async def test_sending(
        cron_context,
        mockserver,
        patch,
        channel_type,
        entity,
        channel_name,
        properties,
):
    sending_id = '00000000000000000000000000000001'
    task_id = 1337

    mock_scheduler(
        sending_id, 'send_to_channel', mockserver, properties, task_id=task_id,
    )
    mock_admin(mockserver, entity, channel_type, channel_name)

    @mockserver.json_handler('ucommunications/driver/sms/send')
    async def _driver_sms_send_handler(request):
        return web.json_response({'code': 'code', 'message': 'message'})

    @mockserver.json_handler('ucommunications/user/sms/send')
    async def _user_sms_send_handler(request):
        return web.json_response({'code': 'code', 'message': 'message'})

    @mockserver.json_handler('/client-notify/v2/bulk-push')
    async def _driver_bulk_push(*_a, **_kw):
        return {'notifications': []}

    @mockserver.json_handler('ucommunications/user/notification/bulk-push')
    async def _user_bulk_push(*_a, **_kw):
        return {}

    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    async def _driver_wall(*_a, **_kw):
        return {'id': 'id'}

    @patch('crm_hub.repositories.process_results.DataLoader.load_to_logbroker')
    async def load_to_logbroker(data, *args, **kwargs):
        pass

    await run_task(patch)

    await check_sending(
        sending_id, cron_context, task_id, load_to_logbroker.calls,
    )


@pytest.mark.config(
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
)
@pytest.mark.parametrize(
    'channel_type, entity, channel_name, properties, sending_id, verify, '
    'control, use_policy',
    [
        (
            'SMS',
            'Driver',
            'driver_sms',
            [
                {
                    'scope_start': 1,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 200,
                    'expired': True,
                },
            ],
            '00000000000000000000000000000004',
            False,
            True,
            True,
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 50},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 50},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'SMS',
            'User',
            'user_sms',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'SMS',
            'User',
            'user_sms',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 50},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 50},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'PUSH',
            'Driver',
            'driver_push',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'PUSH',
            'Driver',
            'driver_push',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 50},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 50},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'PUSH',
            'User',
            'user_push',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'PUSH',
            'User',
            'user_push',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 50},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 50},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'legacywall',
            'Driver',
            'driver_legacywall',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'legacywall',
            'Driver',
            'driver_legacywall',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 50},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 50},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            [
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 20},
                {'scope_start': 1, 'scope_end': 50, 'offset': 0, 'size': 20},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 25},
                {'scope_start': 51, 'scope_end': 100, 'offset': 0, 'size': 25},
                {
                    'scope_start': 101,
                    'scope_end': 150,
                    'offset': 0,
                    'size': 50,
                },
                {
                    'scope_start': 151,
                    'scope_end': 200,
                    'offset': 0,
                    'size': 50,
                },
            ],
            '00000000000000000000000000000002',
            False,
            False,
            True,
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
            '00000000000000000000000000000003',
            True,
            False,
            True,
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
            '00000000000000000000000000000004',
            False,
            True,
            True,
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
            '00000000000000000000000000000005',
            False,
            True,
            False,
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            [{'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200}],
            '00000000000000000000000000000006',
            False,
            False,
            False,
        ),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
async def test_logging(
        cron_context,
        mockserver,
        patch,
        yt_client,
        channel_type,
        entity,
        channel_name,
        properties,
        sending_id,
        verify,
        control,
        use_policy,
):

    mock_scheduler(sending_id, 'send_to_log', mockserver, properties)
    mock_admin(mockserver, entity, channel_type, channel_name)

    yt_path = '//home/taxi-crm/drivers/test/experiments'
    yt_table_path = f'{yt_path}/friday_the_13th_cm'
    yt_client.mkdir(yt_path, recursive=True)
    yt_client.remove(yt_table_path, force=True)
    await run_task(patch)
    expired = properties[0].get('expired', False)
    await check_logging(
        cron_context,
        yt_client,
        yt_table_path,
        verify,
        control,
        use_policy,
        expired=expired,
    )


@pytest.mark.config(
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
)
@pytest.mark.parametrize(
    'task_items, sending_id, pg_table',
    [
        (
            [
                {
                    'id': 1337,
                    'time_delay_ms': 0,
                    'sending_id': '00000000000000000000000000000007',
                    'task_properties': [],
                    'task_ids_to_log': [0, 1, 2],
                },
            ],
            '00000000000000000000000000000007',
            'logging_by_task_id',
        ),
        (
            [
                {
                    'id': 1337,
                    'time_delay_ms': 0,
                    'sending_id': '00000000000000000000000000000008',
                    'task_properties': [],
                    'task_ids_to_log': [0, 1, 2],
                },
                {
                    'id': 1338,
                    'time_delay_ms': 0,
                    'sending_id': '00000000000000000000000000000008',
                    'task_properties': [
                        {
                            'offset': 0,
                            'size': 50,
                            'scope_start': 151,
                            'scope_end': 200,
                        },
                    ],
                },
            ],
            '00000000000000000000000000000008',
            'logging_mixed',
        ),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
async def test_logging_by_task(
        cron_context,
        mockserver,
        patch,
        yt_client,
        task_items,
        sending_id,
        pg_table,
):

    mock_scheduler(
        sending_id, 'send_to_log', mockserver, None, task_items=task_items,
    )
    mock_admin(mockserver, 'Driver', 'SMS', 'driver_sms')

    yt_path = '//home/taxi-crm/drivers/test/experiments'
    yt_table_path = f'{yt_path}/friday_the_13th_cm'
    yt_client.mkdir(yt_path, recursive=True)
    yt_client.remove(yt_table_path, force=True)

    await run_task(patch)
    await check_logging(
        cron_context,
        yt_client,
        yt_table_path,
        False,
        False,
        True,
        pg_table=pg_table,
    )


@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
@pytest.mark.parametrize('sending_successfull', [True, False])
async def test_sending_stop(
        cron_context, mockserver, patch, sending_successfull,
):
    sending_id = '00000000000000000000000000000002'

    mock_scheduler(
        sending_id, 'sending_finished', mockserver, [], sending_successfull,
    )
    await run_task(patch)

    query = (
        f'SELECT state FROM crm_hub.batch_sending WHERE id=\'{sending_id}\''
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        sending_status = await conn.fetchval(query)
    assert sending_status == ('FINISHED' if sending_successfull else 'ERROR')
