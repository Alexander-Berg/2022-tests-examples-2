# pylint: disable=unused-variable,invalid-name,protected-access,C0302
import enum
import json
import typing

from aiohttp import web
import pytest

from crm_hub.generated.custom_unit import run_cron
from crm_hub.logic import experiments_logger


class Action(enum.Enum):
    POLICY = 'POLICY'
    CHANNEL = 'CHANNEL'
    PROMOCODE = 'PROMOCODE'


def mock_policy(mockserver):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message_bulk')
    async def _policy_check(request):
        allowed = []
        for item in request.json['items']:
            allowed.append(bool(int(item['entity_id'][-1]) % 2))
        return mockserver.make_response(status=200, json={'allowed': allowed})


def mock_admin_v2(
        mockserver,
        entity: str,
        actions_list: typing.List[Action],
        channel_name: typing.Optional[str],
        channel_type: typing.Optional[str],
):
    @mockserver.json_handler('crm-admin/v2/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        actions = []
        if Action.CHANNEL in actions_list and channel_name:
            actions.append(
                {
                    'action_name': 'channel',
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
                },
            )
        if Action.POLICY in actions_list and channel_type:
            actions.append({'action_name': 'policy', 'channel': channel_type})

        if Action.PROMOCODE in actions_list:
            actions.append(
                {
                    'action_name': 'promocode',
                    'promocode_settings': {
                        'service': 'eats',
                        'series': 'series_1',
                        'finish_at': '2022-01-31T04:00:00+03:00',
                    },
                },
            )

        result = {
            'name': 'my_name',
            'entity_type': entity,
            'group_type': 'testing',
            'yt_table': 'my_yt_table',
            'yt_test_table': 'my_yt_table_verification',
            'local_control': False,
            'global_control': False,
            'actions': actions,
            'extra_data': {},
            'report_info': {
                'creation_day': 'friday_the_13th',
                'experiment_name': 'experiment_name',
                'experiment_type': 'experiment_type',
                'experiment_id': 'experiment_id',
            },
        }

        if channel_name:
            result['report_info']['channel'] = channel_name

        return result


def mock_scheduler_v2(
        sending_id,
        task_type,
        mockserver,
        properties,
        sending_successfull=None,
        task_items=None,
        task_id=1337,
        step_num=None,
):
    @mockserver.json_handler('/crm-scheduler/v2/report_task_ended')
    async def _notify_scheduler(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/crm-scheduler/v2/get_task_list')
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
        if not task_items and step_num:
            meta_data['task_list'][0]['step_num'] = step_num

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

    await run_cron.main(['crm_hub.daemon.run_daemon_v2', '-t', '0'])


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
            f'SELECT id, actions_states FROM crm_hub.{sending_table}'
        )
        records = await conn.fetch(policy_query)

        passed = filtered = has_task_id = 0
        for record in records:
            if record['actions_states']:
                actions_states = json.loads(record['actions_states'])
                if 'policy' in actions_states:
                    if actions_states['policy']['status'] == 'SUCCESS':
                        passed += 1
                    if actions_states['policy']['status'] == 'SKIP':
                        filtered += 1
                if 'source_task_id' in actions_states['policy']:
                    has_task_id += 1

        assert passed == passed_expected
        assert filtered == filtered_expected

        logbroker_successes = set()
        logbroker_skips = set()
        for logs in logbroker_logs:
            for log in logs['data']:
                assert log.get('action_id') == 1
                if (
                        log['status']
                        == experiments_logger.ActionStatus.SUCCESS.value
                ):
                    logbroker_successes.add(log['unique_entity_id'])
                if (
                        log['status']
                        == experiments_logger.ActionStatus.FILTERED.value
                ):
                    logbroker_skips.add(log['unique_entity_id'])

        assert len(logbroker_successes) == passed_expected
        assert len(logbroker_skips) == filtered_expected

        assert has_task_id == filtered_expected + passed_expected


async def check_sending(channel_name, context, step_num, logbroker_chunks):
    query = 'SELECT * FROM crm_hub.sending_test_table ORDER BY id;'
    async with context.pg.master_pool.acquire() as conn:
        results = await conn.fetch(query)

    skips = successes = 0
    for inx, result in enumerate(results):
        actions_states = result.get('actions_states')
        if not actions_states:
            raise ValueError('results has not actions_states}')
        actions_states = json.loads(result.get('actions_states'))

        channel_state = actions_states.get(channel_name)
        if not channel_state:
            continue

        status = channel_state.get('status')

        if status == 'SUCCESS':
            assert channel_state.get('source_task_id') == 1337
            successes += 1
        else:
            raise ValueError(f'incorrect status for {inx}: {status}')

    logbroker_successes = set()
    logbroker_skips = set()
    logbroker_logs = [
        logbroker_log
        for logbroker_chunk in logbroker_chunks
        for logbroker_log in logbroker_chunk['data']
    ]
    for log in logbroker_logs:
        assert log.get('action_id') == step_num
        assert log.get('properties', {}).get('policy_allowed') is not None
        if log['status'] == experiments_logger.ActionStatus.SUCCESS.value:
            logbroker_successes.add(log['unique_entity_id'])
        if log['status'] == experiments_logger.ActionStatus.FILTERED.value:
            logbroker_skips.add(log['unique_entity_id'])

    assert successes == 100
    assert len(logbroker_successes) == 100
    assert not skips
    assert not logbroker_skips


async def create_sending_table(
        context, load, channel_name: str, table_name: str,
):
    channel_body = json.dumps(
        {
            'channel_name': channel_name,
            'intent': '',
            'sender': '',
            'text': '',
            'action': '',
            'content': '',
            'deeplink': '',
            'code': 100,
            'ttl': 30,
            'collapse_key': '',
            'feed_id': '',
            'send_at': '2020-09-11T10:00:00+03:00',
            'type': '',
            'url': '',
            'title': '',
            'teaser': '',
        },
    )
    action_states = (
        'CASE WHEN i % 2 = 1 THEN '
        '\'{"policy": {"status": "SUCCESS", '
        '"source_task_id": 123}}\'::jsonb '
        'ELSE \'{"policy": {"status": "SKIP", '
        '"reason": "Filtered", '
        '"source_task_id": 123}}\'::jsonb END'
    )
    async with context.pg.master_pool.acquire() as conn:
        await conn.execute(f'DROP TABLE IF EXISTS crm_hub.{table_name};')

        create_query = load('create_sending_table.txt').format(
            table_name=table_name, channel_name=channel_name,
        )
        await conn.execute(create_query)

        insert_query = load('insert_into_sending_table.txt').format(
            table_name=table_name,
            channel_name=channel_name,
            channel_body=channel_body,
            action_states=action_states,
        )
        await conn.execute(insert_query)


async def check_logging(
        context, yt_client, yt_table_path, verify, sending_id, use_policy,
):

    if verify:
        assert not yt_client.exists(yt_table_path)
    else:
        assert yt_client.get(yt_table_path + '/@row_count') == 200
        logs = yt_client.read_table(yt_table_path)
        sent = 100 if use_policy else 200

        assert (
            sum(
                1
                for row in logs
                if row['properties']['communication_status'] == 'sent'
            )
            == sent
        )

    get_table_query = (
        f'SELECT pg_table '
        f'FROM crm_hub.batch_sending '
        f'WHERE id = \'{sending_id}\';'
    )
    async with context.pg.master_pool.acquire() as conn:
        table_result = await conn.fetch(get_table_query)
        table = table_result[0]['pg_table']
        query = f'SELECT * FROM crm_hub.{table} ORDER BY id;'
        results = await conn.fetch(query)

    assert set(map(lambda r: r['was_logged'], results)) == {True}


async def check_sending_stats(context, sending_id):
    query = (
        'SELECT sending_stats '
        'FROM crm_hub.batch_sending '
        f'WHERE id=\'{sending_id}\''
    )
    async with context.pg.master_pool.acquire() as conn:
        sending_stats = await conn.fetchval(query)

    sending_stats = json.loads(sending_stats)
    assert sending_stats.get('planned') == 200
    assert sending_stats.get('denied') == 25
    assert sending_stats.get('failed') == 75
    assert sending_stats.get('sent') == 25
    assert sending_stats.get('skipped') == 75


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'policy_chunk_size': 100,
        'policy_max_connections': 4,
        'policy_use_results': True,
    },
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
    CRM_HUB_SCHEDULER={'deterministic_logs_enabled': True},
    CRM_HUB_ENABLE_BATCH_SENDING_V2={
        'fully_enabled': True,
        'enabled_campaigns': [],
    },
)
@pytest.mark.parametrize(
    'properties',
    [
        [{'scope_start': 1, 'scope_end': 200}],
        [
            {'scope_start': 1, 'scope_end': 50},
            {'scope_start': 51, 'scope_end': 100},
            {'scope_start': 101, 'scope_end': 150},
            {'scope_start': 151, 'scope_end': 200},
        ],
    ],
)
@pytest.mark.parametrize(
    'passed, filtered, sending_id, sending_table, control',
    [
        (
            100,
            100,
            '00000000000000000000000000000000',
            'policy_test_table',
            False,
        ),
        (
            100,
            100,
            '00000000000000000000000000000009',
            'policy_control_test_table',
            True,
        ),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
async def test_policy_check_v2(
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
    task_id = 1337

    @patch('crm_hub.repositories.process_results.DataLoader.load_to_logbroker')
    async def load_to_logbroker(data, *args, **kwargs):
        pass

    mock_scheduler_v2(
        sending_id,
        'filter_step',
        mockserver,
        properties,
        task_id=task_id,
        step_num=1,
    )
    mock_policy(mockserver)
    mock_admin_v2(
        mockserver=mockserver,
        entity='Driver',
        actions_list=[Action.POLICY, Action.CHANNEL],
        channel_type='SMS',
        channel_name='driver_sms',
    )

    await run_task(patch)
    await check_policy(
        passed,
        filtered,
        cron_context,
        task_id,
        sending_table,
        control,
        load_to_logbroker.calls,
    )


@pytest.mark.config(
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
    CRM_HUB_SCHEDULER={'deterministic_logs_enabled': True},
    CRM_HUB_ENABLE_NEW_POMOTIONS={
        'all_enabled': False,
        'partition_enabled': True,
        'campaigns': ['1234'],
    },
    CRM_HUB_ENABLE_BATCH_SENDING_V2={
        'fully_enabled': True,
        'enabled_campaigns': [],
    },
)
@pytest.mark.parametrize(
    'properties',
    [
        [{'scope_start': 1, 'scope_end': 100}],
        [{'offset': 0, 'size': 100, 'source_task_id': 123}],
        [
            {'offset': 0, 'size': 25, 'source_task_id': 123},
            {'offset': 25, 'size': 25, 'source_task_id': 123},
            {'offset': 50, 'size': 25, 'source_task_id': 123},
            {'offset': 75, 'size': 25, 'source_task_id': 123},
        ],
    ],
)
@pytest.mark.parametrize(
    'channel_type, entity, channel_name, sending_id',
    [
        ('SMS', 'Driver', 'driver_sms', '00000000000000000000000000000010'),
        ('SMS', 'User', 'user_sms', '00000000000000000000000000000011'),
        ('PUSH', 'Driver', 'driver_push', '00000000000000000000000000000012'),
        ('PUSH', 'User', 'user_push', '00000000000000000000000000000013'),
        (
            'legacywall',
            'Driver',
            'driver_legacywall',
            '00000000000000000000000000000014',
        ),
        ('SMS', 'Driver', 'driver_sms', '00000000000000000000000000000010'),
        ('promo', 'User', 'user_promo', '00000000000000000000000000000023'),
        ('promo', 'User', 'user_promo', '00000000000000000000000000000001'),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
async def test_sending_v2(
        cron_context,
        load,
        mockserver,
        patch,
        channel_type,
        entity,
        channel_name,
        properties,
        sending_id,
):
    task_id = 1337

    await create_sending_table(
        cron_context, load, channel_name, 'sending_test_table',
    )

    mock_scheduler_v2(
        sending_id,
        'pipe_step',
        mockserver,
        properties,
        task_id=task_id,
        step_num=2,
    )
    mock_admin_v2(
        mockserver=mockserver,
        entity=entity,
        actions_list=[Action.POLICY, Action.CHANNEL],
        channel_type=channel_type,
        channel_name=channel_name,
    )

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

    @mockserver.json_handler('/promotions/admin/promotions/')
    async def _promotions_handler(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/passenger-tags/v1/upload')
    async def _tag_handler(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/promotions/admin/promotions/publish/')
    async def _publish_handler(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/promotions/admin/promotions/unpublish/')
    async def _unpublish_handler(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler(
        '/communications-audience/communications-audience/v1/publish',
    )
    async def _publish_v2_handler(request):
        return mockserver.make_response(
            status=200, json={'id': 'kek', 'audience_info': []},
        )

    @patch('crm_hub.repositories.process_results.DataLoader.load_to_logbroker')
    async def load_to_logbroker(data, *args, **kwargs):
        pass

    await run_task(patch)

    await check_sending(
        channel_name=channel_name,
        context=cron_context,
        logbroker_chunks=load_to_logbroker.calls,
        step_num=2,
    )


@pytest.mark.config(
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
    CRM_HUB_ENABLE_BATCH_SENDING_V2={
        'fully_enabled': True,
        'enabled_campaigns': [],
    },
)
@pytest.mark.parametrize(
    'properties',
    [
        [
            {'offset': 0, 'size': 50, 'source_task_id': 123},
            {'offset': 50, 'size': 50, 'source_task_id': 123},
            {'offset': 100, 'size': 50, 'source_task_id': 123},
            {'offset': 150, 'size': 50, 'source_task_id': 123},
        ],
        [{'offset': 0, 'size': 200, 'source_task_id': 123}],
    ],
)
@pytest.mark.parametrize(
    'channel_type, entity, channel_name, sending_id, verify, '
    'control, use_policy',
    [
        (
            'SMS',
            'Driver',
            'driver_sms',
            '00000000000000000000000000000015',
            False,
            True,
            True,
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            '00000000000000000000000000000016',
            False,
            False,
            True,
        ),
        (
            'SMS',
            'User',
            'user_sms',
            '00000000000000000000000000000017',
            False,
            False,
            True,
        ),
        (
            'PUSH',
            'Driver',
            'driver_push',
            '00000000000000000000000000000018',
            False,
            False,
            True,
        ),
        (
            'PUSH',
            'User',
            'user_push',
            '00000000000000000000000000000019',
            False,
            False,
            True,
        ),
        (
            'legacywall',
            'Driver',
            'driver_legacywall',
            '00000000000000000000000000000020',
            False,
            False,
            True,
        ),
        (
            'SMS',
            'Driver',
            'driver_sms',
            '00000000000000000000000000000022',
            False,
            False,
            False,
        ),
        (
            None,
            'Driver',
            None,
            '00000000000000000000000000000025',
            False,
            False,
            False,
        ),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
async def test_logging_v2(
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
    step_num = 3
    if not use_policy:
        step_num -= 1
    if verify:
        step_num -= 1

    mock_scheduler_v2(
        sending_id, 'pipe_step', mockserver, properties, step_num=step_num,
    )
    actions = [Action.POLICY, Action.CHANNEL]
    if not channel_name:
        actions = [Action.PROMOCODE]
    mock_admin_v2(
        mockserver=mockserver,
        entity=entity,
        actions_list=actions,
        channel_type=channel_type,
        channel_name=channel_name,
    )

    yt_path = '//home/taxi-crm/drivers/test/experiments'
    yt_table_path = f'{yt_path}/friday_the_13th_cm'
    yt_client.mkdir(yt_path, recursive=True)
    yt_client.remove(yt_table_path, force=True)
    await run_task(patch)
    await check_logging(
        context=cron_context,
        yt_client=yt_client,
        yt_table_path=yt_table_path,
        verify=verify,
        sending_id=sending_id,
        use_policy=use_policy,
    )


@pytest.mark.config(
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
    CRM_HUB_ENABLE_BATCH_SENDING_V2={
        'fully_enabled': True,
        'enabled_campaigns': [],
    },
)
@pytest.mark.parametrize(
    'task_items, sending_id, pg_table',
    [
        (
            [
                {
                    'id': 1337,
                    'step_num': 3,
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
                    'step_num': 3,
                    'time_delay_ms': 0,
                    'sending_id': '00000000000000000000000000000008',
                    'task_properties': [],
                    'task_ids_to_log': [0, 1, 2],
                },
                {
                    'id': 1338,
                    'step_num': 3,
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
async def test_logging_by_task_v2(
        cron_context,
        mockserver,
        patch,
        yt_client,
        task_items,
        sending_id,
        pg_table,
):

    mock_scheduler_v2(
        sending_id, 'pipe_step', mockserver, None, task_items=task_items,
    )
    mock_admin_v2(
        mockserver=mockserver,
        entity='Driver',
        actions_list=[Action.POLICY, Action.CHANNEL],
        channel_type='SMS',
        channel_name='driver_sms',
    )

    yt_path = '//home/taxi-crm/drivers/test/experiments'
    yt_table_path = f'{yt_path}/friday_the_13th_cm'
    yt_client.mkdir(yt_path, recursive=True)
    yt_client.remove(yt_table_path, force=True)

    await run_task(patch)
    await check_logging(
        context=cron_context,
        yt_client=yt_client,
        yt_table_path=yt_table_path,
        verify=False,
        sending_id=sending_id,
        use_policy=True,
    )


@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
@pytest.mark.parametrize('sending_successfull', [True, False])
async def test_sending_stop_v2(
        cron_context, mockserver, patch, sending_successfull,
):
    sending_id = '00000000000000000000000000000024'

    mock_scheduler_v2(
        sending_id, 'sending_finished', mockserver, [], sending_successfull,
    )
    await run_task(patch)

    query = (
        f'SELECT state FROM crm_hub.batch_sending WHERE id=\'{sending_id}\''
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        sending_status = await conn.fetchval(query)
    assert sending_status == ('FINISHED' if sending_successfull else 'ERROR')

    await check_sending_stats(context=cron_context, sending_id=sending_id)
