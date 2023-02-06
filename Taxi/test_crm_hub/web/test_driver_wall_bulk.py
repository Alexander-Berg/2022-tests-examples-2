import pytest

from crm_hub.generated.custom_unit import run_cron


def mock_admin(
        mockserver, entity, channel_type, channel_name, template_fields,
):
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
                'action': 'MessageNew',
                'content': 'my_content',
                'deeplink': 'my_deeplink',
                'code': 100,
                'ttl': 30,
                'collapse_key': 'MessageNew:test',
                'feed_id': 'id',
                'send_at': '2020-09-11T10:00:00+03:00',
                'type': 'type',
                **template_fields,
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
):
    task_id = 1337

    @mockserver.json_handler('/crm-scheduler/v1/report_task_ended')
    async def _notify_scheduler(request):
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/crm-scheduler/v1/get_task_list')
    async def _action(request):
        meta_data = {
            'task_type': task_type,
            'task_list': [
                {
                    'id': task_id,
                    'time_delay_ms': 0,
                    'sending_id': sending_id,
                    'task_properties': properties,
                },
            ],
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


@pytest.mark.parametrize(
    'template_fields, personal_fields',
    [
        (
            {
                'text': 'sample text',
                'title': 'sample title',
                'teaser': 'sample teaser',
                'url': 'ya.ru',
                'type': 'type',
            },
            [],
        ),
        (
            {
                'text': 'sample text {driver_uuid}',
                'title': 'sample title',
                'teaser': 'sample teaser',
                'url': 'ya.ru',
                'type': 'type',
            },
            ['text'],
        ),
        (
            {
                'text': 'sample text {driver_uuid}',
                'title': 'sample title {driver_uuid}',
                'teaser': 'sample teaser {driver_uuid}',
                'url': 'ya.ru/{driver_uuid}',
                'type': 'type',
            },
            ['text', 'title', 'teaser', 'url'],
        ),
        (
            {
                'text': 'sample text {driver_uuid}',
                'title': 'sample title {driver_uuid}',
                'teaser': 'sample teaser {driver_uuid}',
                'url': 'ya.ru/{driver_uuid}',
                'type': 'dsat',
            },
            ['text', 'title', 'teaser', 'dsat_action', 'url'],
        ),
        (
            {
                'text': 'sample text\n{driver_uuid}',
                'title': 'sample title',
                'teaser': 'sample teaser',
                'url': 'ya.ru',
                'type': 'type',
            },
            ['text'],
        ),
    ],
)
@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'channel_settings': {
            'driver_legacywall': {
                'channel_policy_allowed': True,
                'chunk_size': 200,
                'cooling_off_limit': 1,
                'cooling_off_time_ms': 500,
                'max_connections': 4,
            },
        },
    },
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
)
@pytest.mark.pgsql('crm_hub', files=['init.sql'])
async def test_driver_wall_bulk(
        mockserver, patch, template_fields, personal_fields,
):
    sending_id = '00000000000000000000000000000000'
    properties = [
        {'scope_start': 1, 'scope_end': 200, 'offset': 0, 'size': 200},
    ]
    sendings_count = 0

    mock_scheduler(sending_id, 'send_to_channel', mockserver, properties)
    mock_admin(
        mockserver,
        'Driver',
        'legacywall',
        'driver_legacywall',
        template_fields,
    )

    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    async def _driver_wall(request):
        nonlocal sendings_count

        data = request.json
        template = data['template']
        drivers = data.get('drivers')
        assert {key: template[key] for key in ('text', 'title', 'teaser')} == {
            key: template_fields[key] for key in ('text', 'title', 'teaser')
        }
        if template_fields['type'] == 'dsat':
            assert template['dsat_action'] == template_fields['url']
        else:
            assert template['url'] == template_fields['url']

        if personal_fields:
            assert len(drivers) == 10
            assert set.union(*map(lambda x: set(x.keys()), drivers)) == set(
                personal_fields + ['driver'],
            )
        else:
            assert len(data['filters']['drivers']) == 10

        sendings_count += 1
        return {'id': 'id'}

    await run_task(patch)

    assert sendings_count == 1
