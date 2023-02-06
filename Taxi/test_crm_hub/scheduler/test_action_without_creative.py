import json

import pytest

from crm_hub.generated.custom_unit import run_cron
from crm_hub.logic import experiments_logger


async def check_actions_result(context, logbroker_logs):
    query = 'SELECT * FROM crm_hub.test_table ORDER BY id;'
    async with context.pg.master_pool.acquire() as conn:
        results = await conn.fetch(query)

    skips = successes = 0
    for inx, result in enumerate(results):
        actions_states = result.get('actions_states')
        if not actions_states:
            raise ValueError('results has not actions_states}')
        actions_states = json.loads(result.get('actions_states'))

        action_state = actions_states.get('promocode') or actions_states.get(
            'user_tags',
        )
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


def mock_admin_v2(
        mockserver, entity, channel_type, is_promocode=False, is_tags=False,
):
    @mockserver.json_handler('crm-admin/v2/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        actions = [{'action_name': 'policy', 'channel': channel_type}]
        if is_promocode:
            actions.append(
                {
                    'action_name': 'promocode',
                    'promocode_settings': {
                        'series': 'series_1',
                        'service': 'eats',
                        'active_days': 5,
                    },
                },
            )
        if is_tags:
            actions.append(
                {
                    'action_name': 'user_tags',
                    'tags': [
                        {
                            'service': 'eats',
                            'tag': 'tag1',
                            'validity_time': {
                                'active_days': 5,
                                'end_time': '12:00',
                            },
                        },
                    ],
                },
            )
        return {
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


def mock_scheduler_v2(
        sending_id,
        task_type,
        mockserver,
        properties,
        task_id,
        step_num=None,
        sending_successfull=None,
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
            ),
        }

        if step_num:
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
    assert sending_stats.get('denied') == 0
    assert sending_stats.get('failed') == 0
    assert sending_stats.get('sent') == 100
    assert sending_stats.get('skipped') == 100


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
    'sending_id, calls_eats_tags, calls_coupons',
    [
        pytest.param(
            '00000000000000000000000000000001', 10, 0, id='only tags action',
        ),
        pytest.param(
            '00000000000000000000000000000002',
            0,
            10,
            id='only promocode action',
        ),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['batch_info.sql'])
async def test_user_tags(
        web_app_client,
        cron_context,
        mockserver,
        patch,
        properties,
        sending_id,
        calls_eats_tags,
        calls_coupons,
):
    task_id = 1337
    mock_scheduler_v2(
        sending_id=sending_id,
        task_type='pipe_step',
        mockserver=mockserver,
        properties=properties,
        task_id=task_id,
        step_num=2,
    )

    mock_admin_v2(
        mockserver=mockserver,
        entity='User',
        channel_type='sms',
        is_promocode=calls_coupons,
        is_tags=calls_eats_tags,
    )

    @mockserver.handler('eats-tags/v2/upload')
    async def _eats_tags(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.handler('coupons/internal/bulk-generate')
    async def _coupons_gen(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.handler('eats-coupons/internal/white-list')
    async def _eats_coupons_white_list(request):
        return mockserver.make_response(status=200, json={})

    @patch('crm_hub.repositories.process_results.DataLoader.load_to_logbroker')
    async def load_to_logbroker(data, *args, **kwargs):
        pass

    await run_task(patch)

    assert _eats_tags.times_called == calls_eats_tags
    assert _coupons_gen.times_called == calls_coupons
    assert _eats_coupons_white_list.times_called == calls_coupons

    await check_actions_result(cron_context, load_to_logbroker.calls)

    mock_scheduler_v2(
        sending_id=sending_id,
        task_type='sending_finished',
        mockserver=mockserver,
        properties=[],
        task_id=1338,
        sending_successfull=True,
    )
    await run_task(patch)

    query = (
        f'SELECT state FROM crm_hub.batch_sending WHERE id=\'{sending_id}\''
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        sending_status = await conn.fetchval(query)
    assert sending_status == 'FINISHED'

    await check_sending_stats(context=cron_context, sending_id=sending_id)
