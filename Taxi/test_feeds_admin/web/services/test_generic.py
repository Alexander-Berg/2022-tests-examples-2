import json

from aiohttp import web
import pytest

from test_feeds_admin import const


async def _get_ids(response):
    assert response.status == 200
    body = await response.json()
    return [item['id'] for item in body['items']]


@pytest.mark.now('2000-01-02T04:00:00')
@pytest.mark.parametrize(
    ['request_file'],
    [
        ('create_request_ok_weekly_schedule.json',),
        ('create_request_ok_schedule_once_fixed_ttl.json',),
        ('create_request_ok_schedule_once_auto_ttl.json',),
        ('create_request_ok_schedule_periodic.json',),
    ],
)
async def test_create_ok(web_app_client, load, request_file):
    request = json.loads(load(request_file))
    response = await web_app_client.post(
        '/v1/create', json=request, headers={'X-Yandex-Login': 'v-belikov'},
    )
    assert response.status == 200
    content = await response.json()
    expected_content = request.copy()
    expected_content.update(
        {'author': 'v-belikov', 'status': 'created', 'run_history': []},
    )
    assert content.pop('id') is not None
    assert content.pop('created') == content.pop('updated')
    assert expected_content == content


@pytest.mark.now('2000-01-02T04:00:00')
@pytest.mark.parametrize(
    ['request_file'], [('create_request_bad_duplicated_recipients.json',)],
)
async def test_create_bad(web_app_client, load, request_file):
    response = await web_app_client.post(
        '/v1/create',
        json=json.loads(load(request_file)),
        headers={'X-Yandex-Login': 'v-belikov'},
    )
    assert response.status == 400


@pytest.mark.now('2000-01-02T04:00:00')
@pytest.mark.config(FEEDS_ADMIN_READONLY=True)
async def test_create_bad_readonly(web_app_client, load):
    request = json.loads(load('create_request_ok_weekly_schedule.json'))
    response = await web_app_client.post(
        '/v1/create', json=request, headers={'X-Yandex-Login': 'v-belikov'},
    )
    assert response.status == 503


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_default.sql'])
@pytest.mark.parametrize(
    ['feed_id', 'response_file'],
    [
        (const.UUID_1, 'get_response_ok_1.json'),
        (const.UUID_2, 'get_response_ok_2.json'),
        (const.UUID_6, 'get_response_ok_6.json'),
    ],
)
async def test_get_ok(web_app_client, load, feed_id, response_file):
    response = await web_app_client.get(
        '/v1/get/', params={'id': feed_id, 'service': 'driver_wall'},
    )
    assert response.status == 200

    content = await response.json()
    content.pop('created')
    content.pop('updated')
    assert content == json.loads(load(response_file))


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_default.sql'])
@pytest.mark.parametrize(
    ['feed_id', 'service', 'status'],
    [(1, 'wrong_target_service', 404), (100500, 'driver_wall', 404)],
)
async def test_get_bad(web_app_client, feed_id, service, status):
    response = await web_app_client.get(
        '/v1/get/', params={'id': feed_id, 'service': service},
    )
    assert response.status == status


@pytest.mark.now('2020-01-05T04:00:00')
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_update.sql'])
@pytest.mark.parametrize(
    ['request_file', 'run_history_file'],
    [
        ('update_ok_1_edit_all.json', 'update_ok_1_run_history.json'),
        ('update_ok_2_edit_payload.json', 'update_ok_2_run_history.json'),
        ('update_ok_3_no_schedule.json', 'update_ok_3_run_history.json'),
        ('update_ok_4_no_schedule.json', 'update_ok_4_run_history.json'),
    ],
)
async def test_update_ok(
        web_app_client,
        patch,
        load,
        mock_driver_wall,
        request_file,
        run_history_file,
):  # pylint: disable=W0612
    request = json.loads(load(request_file))
    run_history = json.loads(load(run_history_file))

    @patch(
        'feeds_admin.generated.service.'
        'stq_client.plugin.QueueClient.reschedule',
    )
    async def reschedule(eta, task_id):
        assert task_id == '1'

    @mock_driver_wall('/internal/driver-wall/v1/remove')
    async def handler(request):  # pylint: disable=W0612
        return web.json_response({'success': True})

    response = await web_app_client.post('/v1/update/', json=request)
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/get/', params={'id': const.UUID_1, 'service': 'driver_wall'},
    )
    feed = await response.json()
    assert feed.pop('author') == 'adomogashev'
    assert feed.pop('status') == 'created'
    assert feed.pop('run_history') == run_history
    assert feed.pop('created') is not None
    assert feed.pop('updated') is not None
    assert feed == request


@pytest.mark.now('2020-01-05T04:00:00')
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_update.sql'])
@pytest.mark.parametrize(
    ['request_file'],
    [
        ('update_bad_1_in_progress.json',),
        ('update_bad_2_deleted.json',),
        ('update_bad_3_schedule_has_no_runs.json',),
        ('update_bad_4_duplicated_recipients.json',),
    ],
)
async def test_update_bad(web_app_client, load, request_file):
    response = await web_app_client.post(
        '/v1/update/', json=json.loads(load(request_file)),
    )
    assert response.status == 400


@pytest.mark.config(FEEDS_ADMIN_READONLY=True)
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_update.sql'])
async def test_update_bad_readonly(web_app_client, load):
    request = json.loads(load('update_ok_1_edit_all.json'))
    response = await web_app_client.post(
        '/v1/update', json=request, headers={'X-Yandex-Login': 'v-belikov'},
    )
    assert response.status == 503


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_purge.sql'])
@pytest.mark.parametrize(
    ['feed_id', 'is_remove_success'],
    [
        (const.UUID_1, True),
        (const.UUID_1, False),
        (const.UUID_2, True),
        (const.UUID_3, True),
    ],
)
async def test_purge_ok(
        web_app_client, mock_driver_wall, feed_id, is_remove_success,
):
    @mock_driver_wall('/internal/driver-wall/v1/remove')
    async def handler(request):  # pylint: disable=W0612
        assert request.json['request_ids'] == [f'{feed_id}_1']
        return web.json_response({'success': is_remove_success})

    response = await web_app_client.post(
        f'/v1/purge/', params={'id': feed_id, 'service': 'driver_wall'},
    )
    assert response.status == 200

    feed = await web_app_client.get(
        f'/v1/get/', params={'id': feed_id, 'service': 'driver_wall'},
    )
    content = await feed.json()
    assert content['status'] == 'finished'


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_purge.sql'])
@pytest.mark.parametrize(
    ['params', 'status'],
    [
        ({'id': 100500, 'service': 'driver_wall'}, 404),
        ({'id': 1, 'service': 'wrong_target_service'}, 404),
    ],
)
async def test_purge_bad(web_app_client, params, status):
    response = await web_app_client.post(f'/v1/purge/', params=params)
    assert response.status == status


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_stop.sql'])
@pytest.mark.parametrize(
    ['feed_id'], [(const.UUID_1,), (const.UUID_2,), (const.UUID_4,)],
)
async def test_stop_ok(web_app_client, feed_id):
    response = await web_app_client.post(
        f'/v1/stop/', params={'id': feed_id, 'service': 'test'},
    )
    assert response.status == 200

    feed = await web_app_client.get(
        f'/v1/get/', params={'id': feed_id, 'service': 'test'},
    )
    content = await feed.json()
    assert content['status'] == 'published'


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_stop.sql'])
@pytest.mark.parametrize(
    ['feed_id', 'service', 'status'],
    [
        (const.UUID_3, 'test', 400),
        ('100500', 'test', 404),
        (const.UUID_1, 'bad', 404),
    ],
)
async def test_stop_bad(web_app_client, feed_id, service, status):
    response = await web_app_client.post(
        f'/v1/stop/', params={'id': feed_id, 'service': service},
    )
    assert response.status == status


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_default.sql'])
@pytest.mark.parametrize(
    ['feed_id'],
    [
        (const.UUID_1,),  # correct, status CREATED
        (const.UUID_5,),  # correct, status FINISHED
    ],
)
async def test_delete_ok(web_app_client, feed_id):
    response = await web_app_client.post(
        f'/v1/delete/', params={'id': feed_id, 'service': 'driver_wall'},
    )
    assert response.status == 200

    feed = await web_app_client.get(
        f'/v1/get/', params={'id': feed_id, 'service': 'driver_wall'},
    )
    content = await feed.json()
    assert content['status'] == 'deleted'


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_default.sql'])
@pytest.mark.parametrize(
    ['feed_id', 'service', 'status'],
    [
        (const.UUID_4, 'driver_wall', 400),
        ('100500', 'driver_wall', 404),
        (const.UUID_1, 'bad', 404),
    ],
)
async def test_delete_bad(web_app_client, feed_id, service, status):
    response = await web_app_client.post(
        f'/v1/delete/', params={'id': feed_id, 'service': service},
    )
    assert response.status == status


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
@pytest.mark.parametrize(
    ['limit', 'skip', 'filters', 'count'],
    [
        (50, 0, None, 4),
        (50, 1, None, 3),
        (50, 100500, None, 0),
        (1, None, None, 1),
        (None, None, {'status': ['created']}, 2),
        (None, None, {'status': ['created', 'error']}, 3),
        (None, None, {'recipients_type': 'yql'}, 2),
        (None, None, {'author': ['adomogashev']}, 1),
        (
            None,
            None,
            {
                'author': ['adomogashev', 'lostpointer'],
                'status': ['created', 'finished'],
            },
            2,
        ),
    ],
)
async def test_list_ok(web_app_client, limit, skip, filters, count):
    response = await web_app_client.post(
        '/v1/list/',
        json={
            'service': 'driver_wall',
            'limit': limit,
            'skip': skip,
            'filters': filters,
        },
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['items']) == count


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_bad_unknown_service(web_app_client):
    response = await web_app_client.post(
        '/v1/list/', json={'service': 'unknown_service'},
    )
    assert response.status == 200
    content = await response.json()
    assert not content['items']


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_services(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={
            'services': ['driver_wall', 'payload-filter'],
            'limit': 2,
            'skip': 0,
            'filters': {'author': ['v-belikov']},
        },
    )
    assert response.status == 200
    data = await response.json()
    assert len(data['items']) == 2
    data.pop('items')
    assert data == {
        'services': ['driver_wall', 'payload-filter'],
        'limit': 2,
        'skip': 0,
        'total': 7,
    }


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_bad_service_and_services(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={
            'service': ['driver_wall'],
            'services': ['payload-filter'],
            'limit': 2,
            'skip': 0,
            'filters': {'author': ['v-belikov']},
        },
    )
    assert response.status == 400


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_payload_filter_equals(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={
            'service': 'payload-filter',
            'filters': {
                'payload': [
                    {
                        'path': 'text',
                        'values': ['equals text'],
                        'operator': 'equals',
                    },
                ],
            },
        },
    )
    assert await _get_ids(response) == [const.UUID_6]


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_payload_filter_contains(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={
            'service': 'payload-filter',
            'filters': {
                'payload': [
                    {
                        'path': 'content.name',
                        'values': ['this', 'name'],
                        'operator': 'contains',
                    },
                ],
            },
        },
    )
    assert await _get_ids(response) == [const.UUID_8, const.UUID_7]


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_payload_filter_multiple(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={
            'service': 'payload-filter',
            'filters': {
                'payload': [
                    {
                        'path': 'type',
                        'values': ['newsletter'],
                        'operator': 'equals',
                    },
                    {
                        'path': 'content.name',
                        'values': ['escaping'],
                        'operator': 'contains',
                    },
                ],
            },
        },
    )
    assert await _get_ids(response) == [const.UUID_9]


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_payload_filter_escaped_quote(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={
            'service': 'payload-filter',
            'filters': {
                'payload': [
                    {
                        'path': 'content.name',
                        'values': ['it\'s'],
                        'operator': 'contains',
                    },
                ],
            },
        },
    )
    assert await _get_ids(response) == [const.UUID_9]


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_payload_filter_array(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={
            'service': 'payload-filter',
            'filters': {
                'payload': [
                    {
                        'path': 'pages.0.name',
                        'values': ['array'],
                        'operator': 'equals',
                    },
                ],
            },
        },
    )
    assert await _get_ids(response) == [const.UUID_10]


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_name_many_search(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={'service': 'driver_wall', 'filters': {'name': 'bar'}},
    )
    assert await _get_ids(response) == [
        const.UUID_5,
        const.UUID_2,
        const.UUID_1,
    ]


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_name_several_words(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={'service': 'driver_wall', 'filters': {'name': 'PaRaM bAr'}},
    )
    assert await _get_ids(response) == [const.UUID_2]


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_name_russian_search(web_app_client):
    response = await web_app_client.post(
        '/v1/list/',
        json={'service': 'driver_wall', 'filters': {'name': 'ба'}},
    )
    assert await _get_ids(response) == [const.UUID_4]
