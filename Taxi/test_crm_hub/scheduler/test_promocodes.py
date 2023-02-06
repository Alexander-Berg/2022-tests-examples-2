# pylint: disable=unused-variable,invalid-name,protected-access,C0302
import hashlib
import json

import pytest

from crm_hub.generated.custom_unit import run_cron
from crm_hub.logic import experiments_logger


def mock_admin_v2(mockserver, entity, channel_type, channel_name):
    @mockserver.json_handler('crm-admin/v2/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        return {
            'name': 'my_name',
            'entity_type': entity,
            'group_type': 'testing',
            'yt_table': 'my_yt_table',
            'yt_test_table': 'my_yt_table_verification',
            'local_control': False,
            'global_control': False,
            'actions': [
                {'action_name': 'policy', 'channel': channel_type},
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
                {
                    'action_name': 'promocode',
                    'promocode_settings': {
                        'series': 'series_1',
                        'service': 'eats',
                        'active_days': 5,
                    },
                },
            ],
            'extra_data': {},
            'report_info': {
                'creation_day': 'friday_the_13th',
                'channel': channel_name,
                'experiment_name': 'experiment_name',
                'experiment_type': 'experiment_type',
                'experiment_id': 'experiment_id',
            },
        }


def mock_scheduler_v2(
        sending_id, task_type, mockserver, properties, task_id, step_num,
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
                        'step_num': step_num,
                    },
                ]
            ),
        }
        return mockserver.make_response(json=meta_data, status=200)


async def run_task(patch):
    @patch('crm_hub.daemon.daemon_runner.DaemonRunner._check_force_exit')
    async def _check_force_exit(*args, **kwargs):
        return True

    await run_cron.main(['crm_hub.daemon.run_daemon_v2', '-t', '0'])


async def check_promocodes(context, logbroker_logs):
    query = 'SELECT * FROM crm_hub.promocodes_test_table ORDER BY id;'
    async with context.pg.master_pool.acquire() as conn:
        results = await conn.fetch(query)

    skips = successes = 0
    for inx, result in enumerate(results):
        actions_states = result.get('actions_states')
        if not actions_states:
            raise ValueError('results has not actions_states}')
        actions_states = json.loads(result.get('actions_states'))

        action_state = actions_states.get('promocode')
        if not action_state:
            continue

        status = action_state.get('status')

        if status == 'SUCCESS':
            assert action_state.get('source_task_id') == 1337
            successes += 1
        else:
            raise ValueError(f'incorrect status for {inx}: {status}')

    logbroker_successes = set()
    logbroker_skips = set()
    for logs in logbroker_logs:
        for log in logs['data']:
            if log['status'] == experiments_logger.ActionStatus.SUCCESS.value:
                logbroker_successes.add(log['unique_entity_id'])
            if log['status'] == experiments_logger.ActionStatus.FILTERED.value:
                logbroker_skips.add(log['unique_entity_id'])

    assert successes == 100
    assert len(logbroker_successes) == 100
    assert not skips
    assert not logbroker_skips


@pytest.mark.config(
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
        [{'scope_start': 0, 'scope_end': 100}],
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
    'sending_id',
    ['00000000000000000000000000000001', '00000000000000000000000000000002'],
)
@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
async def test_promocodes(
        cron_context, mockserver, patch, properties, sending_id,
):
    campaign_id = 123
    group_id = campaign_id
    promocode_service = 'eats'
    series_id = 'series_1'

    task_id = 1337
    mock_scheduler_v2(
        sending_id=sending_id,
        task_type='pipe_step',
        mockserver=mockserver,
        properties=properties,
        task_id=task_id,
        step_num=2,
    )

    mock_admin_v2(mockserver, 'User', 'sms', 'user_sms')

    async def _coupons_request_check(request):
        request_json = request.json

        token_val = f'{campaign_id}_{group_id}_{promocode_service}_{series_id}'
        token = hashlib.md5(token_val.encode()).hexdigest()
        assert request_json.get('token') == token
        assert request_json.get('series_id') == series_id

        users_list = request_json.get('users_list')
        assert len(users_list) >= 1
        assert users_list[0]['yandex_uid'] is not None
        assert users_list[0]['brand_name'] is not None

    async def _eats_coupons_request_check(request):
        request_json = request.json

        assert request_json.get('series_id') == series_id
        yandex_uids = request_json.get('yandex_uids')
        assert len(yandex_uids) >= 1

    @mockserver.handler('coupons/internal/bulk-generate')
    async def _coupons_gen(request):
        await _coupons_request_check(request)
        return mockserver.make_response(status=200, json={})

    @mockserver.handler('eats-coupons/internal/white-list')
    async def _eats_coupons_white_list(request):
        await _eats_coupons_request_check(request)
        return mockserver.make_response(status=200, json={})

    @patch('crm_hub.repositories.process_results.DataLoader.load_to_logbroker')
    async def load_to_logbroker(data, *args, **kwargs):
        pass

    await run_task(patch)

    assert _coupons_gen.times_called == 10
    assert _eats_coupons_white_list.times_called == 10

    await check_promocodes(cron_context, load_to_logbroker.calls)
