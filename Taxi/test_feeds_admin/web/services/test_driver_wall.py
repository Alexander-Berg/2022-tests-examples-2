from aiohttp import web
import pytest

from test_feeds_admin import const


IMAGE_URL_PREFIX = '/driver/v1/driver-wall/image'


def _make_image_url(image_id: str) -> str:
    return f'{IMAGE_URL_PREFIX}/{image_id}.png'


PAYLOAD = {
    'title': 'Заголовок',
    'text': 'Текст **markdown** с {параметрами}',
    'url': 'https://yandex.ru',
    'type': 'newsletter',
    'teaser': 'Текст на ссылке',
    'dom_storage': True,
    'notification_mode': 'normal',
    'important': False,
    'alert': True,
    'format': 'Markdown',
    'url_open_mode': 'browser',
    'image_id': 'image_id',
}

SETTINGS_WITH_IMAGE = {
    'application': 'taximeter',
    'use_wave_sending': False,
    'crm_campaign_id': 'hex',
    'image': {
        'base64': (
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYA'
            'AAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=='
        ),
    },
}

SETTINGS_WITH_IMAGE_URL = {
    'application': 'taximeter',
    'use_wave_sending': False,
    'crm_campaign_id': 'hex',
    'image': {'url': _make_image_url('image_id')},
}

RECIPIENTS = {'type': 'cities', 'recipients_ids': ['Moscow', 'Novosibirsk']}

RUN_HISTORY_ITEM_SUCCESS = {
    'planned_start_at': '2018-06-23T02:11:25+00:00',
    'finished_at': '2018-06-23T02:11:25+00:00',
    'run_id': '10',
    'recipient_count': 2,
    'messages_sent': 0,
    'status': 'success',
}

RUN_HISTORY_ITEM_IN_PROGRESS = {
    'planned_start_at': '2018-06-23T02:11:25+00:00',
    'run_id': '20',
    'recipient_count': 2,
    'messages_sent': 0,
    'status': 'in_progress',
}

RUN_HISTORY_ITEM_NEW = {
    'messages_sent': 0,
    'planned_start_at': '2020-01-06T09:00:00+00:00',
    'run_id': '1',
    'status': 'planned',
}

SCHEDULE = {
    'recurrence': 'schedule',
    'first_publish_at': '2020-01-01T00:00:00+0300',
    'last_publish_at': '2021-01-01T00:00:00+0300',
    'week': [
        {'day': 'monday', 'time': '12:00:00'},
        {'day': 'tuesday', 'time': '14:00:00'},
    ],
    'ttl_seconds': 5 * 24 * 3600,
}

PUBLISH_SCHEDULE = {
    'start_at': '2020-01-01T00:00:00+0300',
    'finish_at': '2021-01-01T00:00:00+0300',
}


@pytest.mark.parametrize(
    'recipients',
    [
        ({'type': 'cities', 'recipients_ids': ['Moscow', 'Novosibirsk']}),
        ({'type': 'countries', 'recipients_ids': ['Russia']}),
        ({'type': 'domains', 'recipients_ids': ['park_id']}),
        ({'type': 'drivers', 'recipients_ids': ['parkid_uuid']}),
        ({'type': 'experiments', 'recipients_ids': ['experiment']}),
        ({'type': 'tags', 'recipients_ids': ['some_tag']}),
    ],
)
@pytest.mark.now('2019-12-01T3:00:00')
async def test_lifecycle(web_app_client, patch, recipients, mock_driver_wall):
    @mock_driver_wall('/internal/driver-wall/v1/upload-image')
    async def handler_upload_image(request):  # pylint: disable=W0612
        return {'id': 'image_id'}

    # Create
    response = await web_app_client.post(
        '/v1/driver-wall/create',
        headers={'X-Yandex-Login': 'v-belikov'},
        json={
            'service': 'driver_wall',
            'name': 'DriverWall',
            'payload': PAYLOAD,
            'settings': SETTINGS_WITH_IMAGE,
            'ticket': 'TAXICRM-1',
        },
    )
    assert response.status == 200
    feed_id = (await response.json())['id']

    # Get
    response = await web_app_client.get(
        '/v1/driver-wall/get',
        params={'service': 'driver_wall', 'id': feed_id},
    )
    assert response.status == 200
    body = await response.json()
    body.pop('created')
    body.pop('updated')
    assert body == {
        'id': feed_id,
        'service': 'driver_wall',
        'name': 'DriverWall',
        'status': 'created',
        'payload': PAYLOAD,
        'settings': SETTINGS_WITH_IMAGE_URL,
        'run_history': [],
        'author': 'v-belikov',
        'ticket': 'TAXICRM-1',
    }

    # Start
    response = await web_app_client.post(
        '/v1/driver-wall/start',
        json={
            'id': feed_id,
            'service': 'driver_wall',
            'recipients': recipients,
            'schedule': SCHEDULE,
        },
    )
    assert response.status == 200

    # Get
    response = await web_app_client.get(
        '/v1/driver-wall/get',
        params={'service': 'driver_wall', 'id': feed_id},
    )
    assert response.status == 200
    body = await response.json()
    body.pop('created')
    body.pop('updated')
    assert body == {
        'id': feed_id,
        'service': 'driver_wall',
        'name': 'DriverWall',
        'status': 'waiting',
        'payload': PAYLOAD,
        'settings': SETTINGS_WITH_IMAGE_URL,
        'run_history': [RUN_HISTORY_ITEM_NEW],
        'author': 'v-belikov',
        'recipients': recipients,
        'schedule': SCHEDULE,
        'ticket': 'TAXICRM-1',
    }


async def test_incorect_image(
        web_app_client, patch, mock_driver_wall, mockserver,
):
    @mock_driver_wall('/internal/driver-wall/v1/upload-image')
    async def handler_upload_image(request):  # pylint: disable=W0612
        return mockserver.make_response('', 400)

    # Create
    response = await web_app_client.post(
        '/v1/driver-wall/create',
        headers={'X-Yandex-Login': 'v-belikov'},
        json={
            'service': 'driver_wall',
            'name': 'DriverWall',
            'payload': PAYLOAD,
            'recipients': {
                'type': 'cities',
                'recipients_ids': ['Moscow', 'Novosibirsk'],
            },
            'settings': SETTINGS_WITH_IMAGE,
            'ticket': 'TAXICRM-1',
        },
    )
    assert response.status == 400


@pytest.mark.now('2019-12-01T3:00:00')
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_publish.sql'])
async def test_publish_get(web_app_client):
    # Publish
    response = await web_app_client.post(
        '/v1/driver-wall/publish',
        headers={'X-Yandex-Login': 'v-belikov'},
        json={
            'id': const.UUID_1,
            'service': 'driver_wall',
            'recipients': RECIPIENTS,
            'schedule': PUBLISH_SCHEDULE,
        },
    )
    assert response.status == 200

    # Get
    response = await web_app_client.get(
        '/v1/driver-wall/get',
        params={'service': 'driver_wall', 'id': const.UUID_1},
    )
    assert response.status == 200
    body = await response.json()
    body.pop('created')
    body.pop('updated')
    assert body == {
        'id': const.UUID_1,
        'service': 'driver_wall',
        'name': 'DriverWall',
        'status': 'waiting',
        'payload': PAYLOAD,
        'run_history': [
            {
                'planned_start_at': '2019-12-31T21:00:00+00:00',
                'run_id': '1',
                'status': 'planned',
                'messages_sent': 0,
            },
        ],
        'settings': SETTINGS_WITH_IMAGE_URL,
        'author': 'v-belikov',
        'ticket': '',
    }


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_get.sql'])
@pytest.mark.parametrize(
    ['id_', 'status', 'run_history_item'],
    [
        (const.UUID_1, 'created', RUN_HISTORY_ITEM_SUCCESS),
        (const.UUID_2, 'in_progress', RUN_HISTORY_ITEM_IN_PROGRESS),
    ],
)
async def test_get(web_app_client, id_, status, run_history_item):
    response = await web_app_client.get(
        '/v1/driver-wall/get', params={'service': 'driver_wall', 'id': id_},
    )

    assert response.status == 200
    body = await response.json()
    assert body == {
        'id': id_,
        'service': 'driver_wall',
        'name': 'DriverWall',
        'status': status,
        'payload': PAYLOAD,
        'recipients': RECIPIENTS,
        'run_history': [run_history_item],
        'settings': SETTINGS_WITH_IMAGE_URL,
        'created': '2019-12-30T00:00:00+0300',
        'updated': '2019-12-31T00:00:00+0300',
        'author': 'v-belikov',
        'ticket': 'TAXICRM-1',
    }


@pytest.mark.now('2019-12-01T3:00:00')
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_get.sql'])
async def test_copy(web_app_client):
    copy_response = await web_app_client.post(
        '/v1/driver-wall/copy',
        headers={'X-Yandex-Login': 'new_author'},
        json={
            'service': 'driver_wall',
            'id': const.UUID_1,
            'crm_campaign_id': 'new_crm_id',
        },
    )

    assert copy_response.status == 200
    copy_body = await copy_response.json()
    target_id = copy_body.pop('id')
    assert target_id != const.UUID_1
    assert copy_body == {}

    get_response = await web_app_client.get(
        '/v1/driver-wall/get',
        params={'service': 'driver_wall', 'id': target_id},
    )
    assert get_response.status == 200
    get_body = await get_response.json()
    assert get_body.pop('updated') != '2019-12-31T00:00:00+0300'
    assert get_body.pop('created') != '2019-12-30T00:00:00+0300'
    assert get_body == {
        'id': target_id,
        'service': 'driver_wall',
        'name': 'DriverWall',
        'status': 'created',
        'payload': PAYLOAD,
        'run_history': [],
        'settings': {
            'application': 'taximeter',
            'use_wave_sending': False,
            'crm_campaign_id': 'new_crm_id',
            'image': {'url': _make_image_url('image_id')},
        },
        'author': 'new_author',
        'ticket': 'TAXICRM-1',
    }


@pytest.mark.now('2019-12-01T3:00:00')
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_default.sql'])
async def test_update(web_app_client, patch):
    # pylint: disable=W0612
    @patch(
        'feeds_admin.generated.service.'
        'stq_client.plugin.QueueClient.reschedule',
    )
    async def reschedule(eta, task_id):
        pass

    response = await web_app_client.post(
        '/v1/driver-wall/update',
        json={
            'id': const.UUID_1,
            'service': 'driver_wall',
            'name': 'Changed name',
            'payload': PAYLOAD,
            'ticket': 'TAXICRM-1',
        },
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/driver-wall/get',
        params={'service': 'driver_wall', 'id': const.UUID_1},
    )
    assert response.status == 200
    body = await response.json()
    assert body.pop('updated') != '2019-12-31T00:00:00+0300'
    assert body == {
        'id': const.UUID_1,
        'service': 'driver_wall',
        'name': 'Changed name',
        'status': 'created',
        'payload': PAYLOAD,
        'recipients': RECIPIENTS,
        'run_history': [],
        'created': '2019-12-30T00:00:00+0300',
        'author': 'v-belikov',
        'ticket': 'TAXICRM-1',
    }


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_stop.sql'])
@pytest.mark.parametrize(
    ['params', 'status'],
    [
        ({'id': const.UUID_1, 'service': 'driver_wall'}, 200),  # correct
        (
            {'id': const.UUID_2, 'service': 'driver_wall'},
            200,
        ),  # incorrect regularity
        (
            {'id': const.UUID_3, 'service': 'driver_wall'},
            400,
        ),  # incorrect status
        (
            {'id': const.UUID_4, 'service': 'driver_wall'},
            200,
        ),  # correct - failed feed
        ({'id': 'incorrect', 'service': 'driver_wall'}, 404),  # incorrect id
        (
            {'id': const.UUID_10, 'service': 'driver_wall'},
            404,
        ),  # unexistent id
        (
            {'id': const.UUID_1, 'service': 'wrong_target_service'},
            400,
        ),  # wrong service
        ({'id': const.UUID_1}, 400),  # without service param
    ],
)
async def test_stop(web_app_client, params, status):
    response = await web_app_client.post(f'/v1/driver-wall/stop/', json=params)
    assert response.status == status

    if status == 200:
        updated_feed = await web_app_client.get(
            f'/v1/driver-wall/get/', params=params,
        )
        content = await updated_feed.json()
        assert content['status'] == 'published'


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_delete.sql'])
async def test_delete(web_app_client):
    response = await web_app_client.post(
        '/v1/driver-wall/delete',
        json={'id': const.UUID_1, 'service': 'driver_wall'},
    )
    assert response.status == 200

    updated_feed = await web_app_client.get(
        '/v1/driver-wall/get',
        params={'id': const.UUID_1, 'service': 'driver_wall'},
    )
    content = await updated_feed.json()
    assert content['status'] == 'deleted'


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_delete.sql'])
async def test_delete_bad_status(web_app_client):
    response = await web_app_client.post(
        '/v1/driver-wall/delete',
        json={'id': const.UUID_2, 'service': 'driver_wall'},
    )
    assert response.status == 400


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_purge.sql'])
@pytest.mark.config(TVM_RULES=[{'dst': 'driver-wall', 'src': 'feeds-admin'}])
@pytest.mark.parametrize(
    ['params', 'run_id', 'status', 'successful_removal'],
    [
        ({'id': const.UUID_1, 'service': 'driver_wall'}, 1, 200, True),
        ({'id': const.UUID_1, 'service': 'driver_wall'}, 1, 200, False),
        ({'id': const.UUID_2, 'service': 'driver_wall'}, 2, 200, True),
        ({'id': const.UUID_3, 'service': 'driver_wall'}, 3, 200, True),
        ({'id': 'incorrect', 'service': 'driver_wall'}, None, 404, None),
        ({'id': const.UUID_10, 'service': 'driver_wall'}, None, 404, None),
        ({'id': const.UUID_1, 'service': 'wrong_service'}, None, 400, None),
        ({'id': const.UUID_1}, None, 400, None),
    ],
)
async def test_purge(
        web_app_client,
        mock_driver_wall,
        params,
        run_id,
        status,
        successful_removal,
):
    @mock_driver_wall('/internal/driver-wall/v1/remove')
    async def handler(request):  # pylint: disable=W0612
        feed_id = params.get('id')
        assert successful_removal is not None
        assert request.json['request_ids'] == [f'{feed_id}_{run_id}']
        return web.json_response({'success': successful_removal})

    response = await web_app_client.post(
        f'/v1/driver-wall/purge/', json=params,
    )
    assert response.status == status

    if status == 200:
        updated_feed = await web_app_client.get(
            f'/v1/driver-wall/get/', params=params,
        )
        content = await updated_feed.json()
        assert content['status'] == 'finished'


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
@pytest.mark.parametrize(
    ['filters', 'ids'],
    [
        ({}, [const.UUID_2]),
        (
            {'show_crm': True, 'type': 'newsletter'},
            [const.UUID_3, const.UUID_2, const.UUID_1],
        ),
        (
            {'status': 'created', 'show_crm': True, 'type': 'newsletter'},
            [const.UUID_2, const.UUID_1],
        ),
        (
            {'status': 'in_progress', 'show_crm': True, 'type': 'newsletter'},
            [const.UUID_3],
        ),
        ({'show_crm': True, 'type': 'survey'}, [const.UUID_4]),
    ],
)
async def test_list(web_app_client, filters, ids):
    response = await web_app_client.post(
        '/v1/driver-wall/list',
        json={'service': 'driver_wall', 'filters': filters},
    )
    assert await _get_ids(response) == ids


async def _get_ids(response):
    assert response.status == 200
    body = await response.json()
    return [item['id'] for item in body['items']]


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_list.sql'])
async def test_list_format(web_app_client):
    response = await web_app_client.post(
        '/v1/driver-wall/list',
        json={
            'service': 'driver_wall',
            'filters': {
                'status': 'in_progress',
                'show_crm': True,
                'type': 'newsletter',
            },
        },
    )
    body = await response.json()
    assert body['total'] == 1
    assert body['items']
    result = body['items'][0]
    assert result == {
        'id': const.UUID_3,
        'service': 'driver_wall',
        'name': 'DriverWall',
        'status': 'in_progress',
        'author': 'v-belikov',
        'created': '2021-12-30T00:00:00+0300',
        'type': 'newsletter',
        'application': 'taximeter',
        'recipients_type': 'cities',
        'recipients_count': 2,
        'recipients_ids': ['Moscow', 'Novosibirsk'],
    }
