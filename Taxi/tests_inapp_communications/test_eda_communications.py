import copy

import pytest

DEFAULT_HEADERS = {
    'X-Request-Application': 'app_name=android',
    'X-Request-Language': 'ru',
    'X-YaTaxi-UserId': 'user_id_1',
    'X-YaTaxi-PhoneId': 'phone_id_1',
    'X-AppMetrica-UUID': 'appmetrica_uid',
}

DEFAULT_REQUEST = {
    'device_id': 'device_id1',
    'application': {'version': '1.2.4', 'platform': 'eda_desktop_web'},
    'state': {
        'point': {'latitude': 55.73552, 'longitude': 37.642474},
        'places': [{'id': 123321}],
        'brands': [{'id': 777}],
        'collections': [{'slug': 'slug'}],
    },
}

PLACE_BANNER = {
    'id': 1,
    'type': 'place',
    'place_id': 123321,
    'priority': 4,
    'payload': {
        'pages': [
            {
                'images': [
                    {'platform': 'web', 'theme': 'light', 'url': 'url'},
                    {'platform': 'web', 'theme': 'dark', 'url': ''},
                    {'platform': 'mobile', 'theme': 'light', 'url': 'url'},
                    {'platform': 'mobile', 'theme': 'dark', 'url': ''},
                ],
            },
        ],
    },
}

BRAND_BANNER = {
    'id': 4,
    'type': 'brand',
    'brand_id': 777,
    'priority': 4,
    'payload': {
        'pages': [
            {
                'images': [
                    {'platform': 'web', 'theme': 'light', 'url': 'url'},
                    {'platform': 'web', 'theme': 'dark', 'url': ''},
                    {'platform': 'mobile', 'theme': 'light', 'url': 'url'},
                    {'platform': 'mobile', 'theme': 'dark', 'url': ''},
                ],
            },
        ],
    },
}

COLLECTION_BANNER = {
    'id': 1000000,
    'type': 'collection',
    'collection_slug': 'slug',
    'description': 'description',
    'priority': 4,
    'url': 'url',
    'app_url': 'app_url',
    'region_id': 333,
    'payload': {
        'pages': [
            {
                'images': [
                    {'platform': 'web', 'theme': 'light', 'url': 'url'},
                    {'platform': 'web', 'theme': 'dark', 'url': ''},
                    {'platform': 'mobile', 'theme': 'light', 'url': 'url'},
                    {'platform': 'mobile', 'theme': 'dark', 'url': ''},
                ],
            },
        ],
    },
}


@pytest.mark.parametrize(
    ('promotions_response',),
    [
        ('default_promotions_service_response.json',),
        ('promotions_service_response_banners.json',),
    ],
)
@pytest.mark.experiments3(filename='exp3_eda_banners.json')
async def test_ok(
        taxi_inapp_communications, mockserver, load_json, promotions_response,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json(promotions_response)

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/eda-communications',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    if promotions_response == 'default_promotions_service_response.json':
        resp = {'banners': [PLACE_BANNER]}
    else:
        resp = {'banners': [PLACE_BANNER, BRAND_BANNER, COLLECTION_BANNER]}
    assert sorted(response.json()['banners'], key=lambda i: i['id']) == sorted(
        resp['banners'], key=lambda i: i['id'],
    )


@pytest.mark.parametrize(
    'phone_id, is_in_test',
    [('phone_id_1', True), ('phone_id_not_in_test_publish', False)],
)
@pytest.mark.experiments3(filename='exp3_test_publish.json')
async def test_test_publish(
        taxi_inapp_communications, phone_id, is_in_test, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['X-YaTaxi-PhoneId'] = phone_id
    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/eda-communications',
        json=DEFAULT_REQUEST,
        headers=headers,
    )

    assert response.status == 200, response.text
    banners = response.json()['banners']
    assert len(banners) == (1 if is_in_test else 0)


@pytest.mark.experiments3(filename='exp3_eda_banners.json')
@pytest.mark.config(INAPP_FEEDS_CONTROL={'enabled': True})
async def test_feeds_integration(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_banners.json')

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    @mockserver.json_handler('/feeds/v1/fetch')
    def _mock_feeds(request):
        return load_json('feeds_eda_banners.json')

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/eda-communications',
        json=DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert _mock_feeds.times_called == 1
    assert response.status == 200
    banners = {
        (banner['id'], banner.get('description'))
        for banner in response.json()['banners']
    }
    assert banners == {
        (1, 'feeds_banner_1_overwrites_promotions'),
        (4, None),
        (30, 'feeds_banner_30'),
        (1000000, 'description'),
    }
