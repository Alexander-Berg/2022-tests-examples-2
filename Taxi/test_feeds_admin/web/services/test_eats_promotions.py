# pylint: disable=protected-access
import copy
import json

from aiohttp import web
import pytest

from feeds_admin.services import eats_promotions


STORY = 'eats-promotions-story'
FULLSCREEN = 'eats-promotions-fullscreen'
BANNER = 'eats-promotions-banner'
INFORMER = 'eats-promotions-informer'

STORY_PAYLOAD = 'story_payload.json'
FULLSCREEN_PAYLOAD = 'fullscreen_payload.json'
BANNER_PAYLOAD = 'banner_payload.json'
BANNER_ADS_PAYLOAD = 'banner_ads_payload.json'
BANNER_PAYLOAD_WITH_POPUP = 'banner_payload_with_popup.json'
BANNER_ADS_DIRECT_PAYLOAD = 'banner_ads_direct_payload.json'
INFORMER_PAYLOAD = 'informer_payload.json'
INFORMER_BACKGROUND_PAYLOAD = 'background_informer_payload.json'

STORY_SETTINGS = 'story_settings.json'
CATEGORY_STORY_SETTINGS = 'category_story_settings.json'
BANNER_SETTINGS = 'banner_settings.json'
BANNER_SETTINGS_HIDE_COUNTER = 'banner_settings_hide_counter.json'

BRAND_BANNER_SETTINGS = 'brand_banner_settings.json'

INFO = {'type': 'info'}
BRANDS = {'type': 'brand', 'brands': [1, 2, 3]}
BRAND_BANNER = {
    'type': 'brand',
    'brands': [4],
    'menu_categories': ['category1'],
}
COLLECTIONS = {'type': 'collection', 'collections': ['slug1']}
COLLECTIONS_HIDE_COUNTER = {
    'type': 'collection',
    'collections': ['slug2'],
    'hide_counter': True,
}

YQL_RECIPIENTS = {'recipient_type': 'yql', 'yql_link': 'some_link'}


def _validate_feeds_create_request(
        request, service, feed_id, settings, payload,
):
    data = request.json['items'][0]

    payload = copy.deepcopy(payload)
    eats_promotions._format_deeplinks(payload)
    eats_promotions._format_recipients(settings, payload)
    if service == BANNER:
        payload['banner_id'] = eats_promotions.make_banner_id(feed_id)
    payload['start_date'] = '2019-08-25T21:00:00+00:00'
    payload['end_date'] = '2050-08-29T21:00:00+00:00'
    payload['experiment'] = 'my_experiment'
    assert data['payload'] == payload

    assert data['channels'] == [
        {'channel': 'experiment:my_experiment', 'feed_id': feed_id},
    ]


@pytest.mark.parametrize(
    'service,payload_file,settings_file',
    [
        (STORY, STORY_PAYLOAD, STORY_SETTINGS),
        (STORY, STORY_PAYLOAD, CATEGORY_STORY_SETTINGS),
        (FULLSCREEN, FULLSCREEN_PAYLOAD, None),
        (BANNER, BANNER_PAYLOAD, BANNER_SETTINGS),
        (BANNER, BANNER_PAYLOAD, BRAND_BANNER_SETTINGS),
        (STORY, STORY_PAYLOAD, STORY_SETTINGS),
        (BANNER, BANNER_ADS_PAYLOAD, BANNER_SETTINGS),
        (BANNER, BANNER_ADS_DIRECT_PAYLOAD, BANNER_SETTINGS),
        (BANNER, BANNER_PAYLOAD_WITH_POPUP, BANNER_SETTINGS),
        (INFORMER, INFORMER_PAYLOAD, None),
        (INFORMER, INFORMER_BACKGROUND_PAYLOAD, None),
    ],
)
@pytest.mark.config(
    FEEDS_ADMIN_SERVICES={
        '__default__': {'max_channels_for_immediate_publish': 3},
    },
)
async def test_lifecycle(
        web_app_client,
        mock_feeds,
        patch,
        testpoint,
        load,
        service,
        payload_file,
        settings_file,
):
    payload = json.loads(load(payload_file))
    settings = json.loads(load(settings_file)) if settings_file else None

    @patch('feeds_admin.actions.publish._is_publish_through_stq')
    def _is_publish_through_stq(*args, **kwargs):  # pylint: disable=W0612
        return False

    @mock_feeds('/v1/batch/create')
    async def feeds_create(request):  # pylint: disable=W0612
        nonlocal feed_id
        _validate_feeds_create_request(
            request, service, feed_id, settings, payload,
        )
        return web.json_response({'items': []})

    @mock_feeds('/v1/batch/remove_by_request_id')
    async def feeds_remove_by_request_id(request):  # pylint: disable=W0612
        return web.json_response({'statuses': {}})

    @testpoint('actions::create')
    def actions_create(data):  # pylint: disable=W0612
        pass

    # Create
    response = await web_app_client.post(
        '/v1/eats-promotions/create',
        headers={'X-Yandex-Login': 'v-belikov'},
        json={
            'service': service,
            'name': 'Eats Promo',
            'payload': payload,
            'settings': settings,
        },
    )
    assert response.status == 200
    feed_id = (await response.json())['id']

    # Publish
    params = {
        'id': feed_id,
        'service': service,
        'schedule': {
            'recurrence': 'once',
            'ttl_auto': True,
            'first_publish_at': '2019-08-26T00:00:00+0300',
            'last_publish_at': '2050-08-30T00:00:00+0300',
        },
        'experiment': 'my_experiment',
    }
    response = await web_app_client.post(
        '/v1/eats-promotions/publish', json=params,
    )
    assert response.status == 200

    # Unpublish
    response = await web_app_client.post(
        '/v1/eats-promotions/unpublish',
        json={'service': service, 'id': feed_id},
    )
    assert response.status == 200

    # Archive
    response = await web_app_client.post(
        '/v1/eats-promotions/archive',
        json={'service': service, 'id': feed_id},
    )
    assert response.status == 200

    # Get
    response = await web_app_client.get(
        '/v1/eats-promotions/get', params={'service': service, 'id': feed_id},
    )
    assert response.status == 200
    body = await response.json()
    body.pop('created')
    body.pop('updated')
    if settings is not None:
        if service == BANNER:
            assert body['settings'].pop('banner_id')
        assert body.pop('settings') == settings
    assert body.pop('experiment') == 'my_experiment'
    assert body == {
        'id': feed_id,
        'service': service,
        'name': 'Eats Promo',
        'status': 'deleted',
        'payload': payload,
        'author': 'v-belikov',
        'schedule': {
            'recurrence': 'once',
            'ttl_auto': True,
            'first_publish_at': '2019-08-26T00:00:00+0300',
            'last_publish_at': '2050-08-30T00:00:00+0300',
        },
    }
