import json

from aiohttp import web
import pytest


@pytest.mark.parametrize(
    'promotion_type,payload_file,settings_file',
    [
        ('taxi-promotions-story', 'story_payload.json', 'story_settings.json'),
        (
            'taxi-promotions-eda_banner',
            'eda_banner_payload.json',
            'eda_banner_settings.json',
        ),
    ],
    ids=('story', 'eda-banner'),
)
@pytest.mark.config(
    FEEDS_ADMIN_SERVICES={
        '__default__': {'max_channels_for_immediate_publish': 3},
    },
)
async def test_promo_lifecycle(
        web_app_client,
        patch,
        load,
        mock_feeds,
        promotion_type,
        payload_file,
        settings_file,
):
    @mock_feeds('/v1/batch/create')
    async def feeds_create(request):  # pylint: disable=W0612
        item = request.json['items'][0]
        return web.json_response(
            data={
                'items': [
                    {
                        'service': item['service'],
                        'feed_ids': {item['service']: 'feeds_feed_id'},
                        'filtered': [],
                    },
                ],
            },
        )

    @mock_feeds('/v1/batch/remove_by_request_id')
    async def feeds_remove_by_request_id(request):  # pylint: disable=W0612
        return web.json_response({'statuses': {}})

    # Test simulates typical lifecycle of promotion:
    # created -> update -> get -> publish -> unpublish

    payload = json.loads(load(payload_file))
    settings = json.loads(load(settings_file))

    # Create
    response = await web_app_client.post(
        '/v1/taxi-promotions/create',
        headers={'X-Yandex-Login': 'v-belikov'},
        json={
            'service': promotion_type,
            'name': 'Taxi Promo',
            'payload': payload,
            'settings': settings,
        },
    )
    assert response.status == 200
    promotion_id = (await response.json())['id']

    # Update
    response = await web_app_client.post(
        '/v1/taxi-promotions/update',
        json={
            'id': promotion_id,
            'service': promotion_type,
            'name': 'New Taxi Promo',
            'payload': payload,
            'settings': settings,
        },
    )
    assert response.status == 200

    # Get
    response = await web_app_client.get(
        '/v1/taxi-promotions/get',
        params={'id': promotion_id, 'service': promotion_type},
    )
    assert response.status == 200
    promo = await response.json()
    promo.pop('created')
    promo.pop('updated')
    assert promo == {
        'id': promotion_id,
        'service': promotion_type,
        'name': 'New Taxi Promo',
        'payload': payload,
        'settings': settings,
        'author': 'v-belikov',
        'status': 'created',
    }

    # Publish
    response = await web_app_client.post(
        '/v1/taxi-promotions/publish',
        json={
            'id': promotion_id,
            'service': promotion_type,
            'recipients': {'experiment': 'new_users'},
            'schedule': {
                'start_at': '2020-01-01T00:00:00+0300',
                'finish_at': '2030-01-01T00:00:00+0300',
            },
        },
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/taxi-promotions/get',
        params={'id': promotion_id, 'service': promotion_type},
    )
    assert response.status == 200
    assert (await response.json())['status'] == 'published'

    # List
    response = await web_app_client.post(
        '/v1/taxi-promotions/list',
        json={
            'service': promotion_type,
            'name': 'promo',
            'status': 'published',
            'offset': 0,
            'limit': 3,
        },
    )
    assert response.status == 200
    items = (await response.json())['items']
    assert len(items) == 1
    assert items[0]['name'] == 'New Taxi Promo'
    assert items[0].get('promotion_id') is not None

    # Unpublish
    response = await web_app_client.post(
        '/v1/taxi-promotions/unpublish',
        json={'id': promotion_id, 'service': promotion_type},
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/taxi-promotions/get',
        params={'id': promotion_id, 'service': promotion_type},
    )
    assert response.status == 200
    assert (await response.json())['status'] == 'stopped'

    # Archive
    response = await web_app_client.post(
        '/v1/taxi-promotions/archive',
        json={'id': promotion_id, 'service': promotion_type},
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/taxi-promotions/get',
        params={'id': promotion_id, 'service': promotion_type},
    )
    assert response.status == 200
    assert (await response.json())['status'] == 'archived'
