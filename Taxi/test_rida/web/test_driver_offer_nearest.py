import datetime

import pytest

from test_rida import experiments_utils
from test_rida import helpers
from test_rida import maps_utils


NOW = datetime.datetime(2020, 2, 26, 13, 50)


@pytest.mark.now(NOW.isoformat())
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@pytest.mark.translations()
@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_offer_count'],
    [
        pytest.param({'position': [56.45, 45.56]}, 400, 0, id='old-way'),
        pytest.param(
            {'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
            200,
            2,
            id='new-way',
        ),
        pytest.param(
            {
                'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
                'position': [56.45, 45.56],
            },
            200,
            2,
            id='mixed-way',
        ),
        pytest.param({}, 400, 0, id='empty-way'),
        pytest.param(
            {'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
            200,
            0,
            marks=experiments_utils.get_driver_dispatch_exp(
                max_search_distance_meters=50,
            ),
            id='0-offers-in-zone',
        ),
        pytest.param(
            {'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
            200,
            2,
            marks=experiments_utils.get_driver_dispatch_exp(),
            id='2-offers-in-zone',
        ),
    ],
)
@pytest.mark.filldb()
async def test_driver_offer_nearest(
        request_body,
        taxi_rida_web,
        expected_status: int,
        expected_offer_count: int,
):
    response = await taxi_rida_web.post(
        '/v3/driver/offer/nearest',
        headers=helpers.get_auth_headers(user_id=1234),
        json=request_body,
    )
    assert response.status == expected_status
    if expected_status == 200:
        data = await response.json()
        offers = data['data']['offers']
        assert len(offers) == expected_offer_count


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'strategy',
    [
        pytest.param(
            'gmaps_with_traffic',
            marks=[
                experiments_utils.get_distance_info_config(
                    'gmaps_with_traffic', 'v3/driver/offer/nearest',
                ),
            ],
        ),
        pytest.param(
            'ruler',
            marks=[
                experiments_utils.get_distance_info_config(
                    'ruler', 'v3/driver/offer/nearest',
                ),
            ],
        ),
    ],
)
@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.filldb()
async def test_driver_offer_nearest_distance_to_offer(
        taxi_rida_web, mockserver, strategy,
):
    await taxi_rida_web.invalidate_caches()

    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(
                distance=1805, duration=20,
            ),
        )

    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/driver/offer/nearest',
        headers=headers,
        json={'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
    )
    assert response.status == 200
    data = await response.json()
    offers = data['data']['offers']
    if strategy == 'gmaps_with_traffic':
        assert offers[0]['driver_to_point_a_route']['distance'] == '2 km'
        assert _mock_google_maps.times_called == len(offers * 2)
    else:
        assert offers[0]['driver_to_point_a_route']['distance'] == '108 m'
        assert _mock_google_maps.times_called == 0


@pytest.mark.now(NOW.isoformat())
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.translations(
    rida={
        'default_driver_suggested_price': {'en': 'DEFAULT PRICE'},
        'default_driver_suggested_price_comment': {'en': 'DEFAULT COMMENT'},
    },
)
@pytest.mark.client_experiments3(
    consumer='rida',
    config_name='rida_driver_suggested_price',
    args=experiments_utils.get_default_user_args(),
    value={
        'default_view': {
            'suggested_price_tk': 'default_driver_suggested_price',
            'comment_tk': 'default_driver_suggested_price_comment',
        },
        'conditions': [],
    },
)
async def test_driver_suggested_price_exp(web_app, web_app_client):
    zone_manager = web_app['context'].zone_settings_manager
    assert (
        len(  # pylint: disable=len-as-condition
            zone_manager._cached_zone_settings,  # pylint: disable=W0212
        )
        == 0
    )

    response = await web_app_client.post(
        '/v3/driver/offer/nearest',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
    )
    assert response.status == 200
    data = await response.json()
    offers = data['data']['offers']
    assert len(offers) == 2
    expected_additional_info = [
        {'type': 1, 'data': {'text': 'DEFAULT PRICE', 'color': '#000000'}},
        {'type': 1, 'data': {'text': 'DEFAULT COMMENT', 'color': '#000000'}},
        {'type': 101, 'data': {}},
    ]
    for offer in offers:
        assert offer['additional_info'] == expected_additional_info
    assert (
        len(zone_manager._cached_zone_settings) == 1  # pylint: disable=W0212
    )


@pytest.mark.now(NOW.isoformat())
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
async def test_driver_offer_nearest_can_make_bid(taxi_rida_web):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/driver/offer/nearest',
        headers=headers,
        json={'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
    )
    assert response.status == 200
    data = await response.json()
    offers = data['data']['offers']
    assert offers, 'offers are empty'
    for offer in offers:
        assert 'can_make_bid' in offer


@pytest.mark.now(NOW.isoformat())
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
async def test_driver_offer_nearest_there_is_a_pending_bid(
        taxi_rida_web, mongodb,
):
    mongodb.rida_bids.update(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
        {'$set': {'bid_status': 'PENDING'}},
    )
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/driver/offer/nearest',
        headers=headers,
        json={'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
    )
    assert response.status == 200
    data = await response.json()
    offers = data['data']['offers']
    assert len(offers) == 1


@pytest.mark.now(NOW.isoformat())
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@pytest.mark.parametrize(
    ['supported_features', 'expected_offers_len'],
    [
        pytest.param(['multiple_bids'], 2, id='multiple_bids'),
        pytest.param(['unknown'], 1, id='unknown_supported_features'),
        pytest.param([], 1, id='empty_supported_features'),
    ],
)
async def test_driver_offer_nearest_multiple_bids(
        taxi_rida_web, mongodb, supported_features, expected_offers_len,
):
    mongodb.rida_bids.update(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
        {'$set': {'bid_status': 'EXPIRED'}},
    )
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/driver/offer/nearest',
        headers=headers,
        json={
            'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
            'supported_features': supported_features,
        },
    )
    assert response.status == 200
    data = await response.json()
    offers = data['data']['offers']
    assert len(offers) == expected_offers_len


PRICE_VALIDATION_EXP_ARGS = experiments_utils.PriceValidationSettingsExpArgs(
    country_id=2,
    zone_id=0,
    is_driver=True,
    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
    device_uuid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
)


@pytest.mark.now(NOW.isoformat())
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@pytest.mark.parametrize(
    ['expected_min_value', 'expected_max_value'],
    [
        pytest.param(0, 111200, id='price_restrictions_exp_disabled'),
        pytest.param(
            800,
            1400,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS,
                bid_min_value=800,
                bid_max_value=1400,
            ),
            id='price_restrictions_exp_static_value_borders',
        ),
        pytest.param(
            900,
            1300,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS,
                bid_min_percent=0.8,
                bid_max_percent=1.2,
            ),
            id='price_restrictions_exp_percent_value_borders',
        ),
    ],
)
async def test_bid_settings(
        web_app_client, expected_min_value: float, expected_max_value: float,
):
    response = await web_app_client.post(
        '/v3/driver/offer/nearest',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
    )
    assert response.status == 200
    data = await response.json()
    offers = data['data']['offers']
    expected_bid_settings = {
        'button_text_template': 'Accept for {price} NGN',
        'button_text_price_key': '{price}',
        'default_price': 1111.59,
        'is_price_change_allowed': True,
        'min_price': expected_min_value,
        'max_price': expected_max_value,
        'additional_info': [],
    }
    assert offers
    for offer in offers:
        assert 'bid_settings' in offer
        assert offer['bid_settings'] == expected_bid_settings


@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@pytest.mark.parametrize(
    'expected_offer_count',
    [
        pytest.param(
            2,
            marks=[
                pytest.mark.now(NOW.isoformat()),
                experiments_utils.get_driver_dispatch_exp(
                    driver_position_last_updated_ttl_seconds=100,
                ),
            ],
            id='driver_position_is_fresh',
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.now(
                    (NOW + datetime.timedelta(seconds=105)).isoformat(),
                ),
                experiments_utils.get_driver_dispatch_exp(
                    driver_position_last_updated_ttl_seconds=100,
                ),
            ],
            id='driver_position_is_outdated',
        ),
    ],
)
async def test_outdated_position(web_app_client, expected_offer_count: int):
    response = await web_app_client.post(
        '/v3/driver/offer/nearest',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
    )
    assert response.status == 200
    data = await response.json()
    offers = data['data']['offers']
    assert len(offers) == expected_offer_count


@pytest.mark.now(NOW.isoformat())
@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/nearest')
@pytest.mark.config(
    RIDA_SETTINGS={
        'bid_ttl_seconds': 60,
        'driver_position_last_updated_ttl_seconds': 1800,
        'expire_after_seconds': 120,
        'expire_time_driver_offer_hours': 12,
        'max_search_distance_meters': 7000,
        'nearest_drivers_limit': 50,
        'nearest_offers_limit': 1,
        'offer_ttl_seconds': 300,
        'remove_bids_on_complete': True,
        'remove_offers_on_complete': True,
    },
)
async def test_expired_offers(taxi_rida_web, mongodb):
    mongodb.rida_offers.update(
        {'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F'},
        {'$set': {'expired_at': datetime.datetime(2007, 1, 1)}},
    )
    response = await taxi_rida_web.post(
        '/v3/driver/offer/nearest',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'driver_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'},
    )
    assert response.status == 200
    data = await response.json()
    offers = data['data']['offers']
    assert len(offers) == 1
