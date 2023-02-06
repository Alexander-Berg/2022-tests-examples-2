import datetime
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from rida import consts
from test_rida import experiments_utils
from test_rida import helpers
from test_rida import maps_utils


_NOW = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
USER_GUID = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5J'
PRICE_VALIDATION_EXP_ARGS = experiments_utils.PriceValidationSettingsExpArgs(
    country_id=12,
    zone_id=1,
    is_driver=False,
    user_guid=USER_GUID,
    device_uuid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
)


@pytest.mark.mongodb_collections('rida_offers')
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_pg_offer.sql'])
@pytest.mark.parametrize(
    ['offer_guid', 'expected_status'],
    [
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F', 200, id='mongo_offer',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', 200, id='pg_offer',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFAAAAA', 404, id='offer_not_found',
        ),
    ],
)
async def test_user_offer_info(
        taxi_rida_web, offer_guid: str, expected_status: int,
):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/user/offer/info',
        headers=headers,
        json={'offer_guid': offer_guid},
    )
    assert response.status == expected_status
    if expected_status == 200:
        offer = (await response.json())['data']['offer']
        assert 'expired_after' in offer
        if 'driver' in offer:
            assert 'vehicle' in offer['driver']
            vehicle = offer['driver']['vehicle']
            color_link = vehicle['vehicle_color_custom_color_image']
            assert color_link.startswith(
                'https://api.rida.app/images/vehicle_color/',
            )


@pytest.mark.parametrize(
    ['eta_exists', 'eta', 'expected_eta'],
    [
        pytest.param(True, 10, 10, id='saved_eta'),
        pytest.param(True, None, 71975, id='eta_is_none'),
        pytest.param(False, None, 71975, id='restored_eta'),
    ],
)
async def test_user_info_calc_eta(
        taxi_rida_web, mongodb, eta_exists, eta, expected_eta,
):
    if eta_exists:
        mongodb.rida_bids.update(
            {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G'},
            {'$set': {'eta_seconds': eta}},
        )
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/user/offer/info',
        headers=headers,
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    bids = offer['bids']
    assert len(bids) == 1
    bid = bids[0]
    assert bid['eta_seconds'] == expected_eta


@pytest.mark.mongodb_collections('rida_offers')
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_pg_offer.sql'])
@pytest.mark.filldb()
@pytest.mark.parametrize(
    ['offer_guid', 'need_count_stats', 'expected_status'],
    [
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F', True, 200, id='happy_path',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFAAAAA',
            False,
            404,
            id='offer_not_found',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAXXX',
            False,
            200,
            id='already_canceled',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
            False,
            200,
            id='offer_in_pg',
        ),
    ],
)
async def test_user_offer_cancel(
        web_app,
        web_app_client,
        get_stats_by_label_values,
        offer_guid: str,
        need_count_stats: bool,
        expected_status: int,
):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await web_app_client.post(
        '/v3/user/offer/cancel',
        headers=headers,
        json={'offer_guid': offer_guid, 'cancel_reason_id': 1},
    )
    assert response.status == expected_status
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'offers.status_change'},
    )
    if need_count_stats:
        assert stats == [
            {
                'kind': 'IGAUGE',
                'labels': {
                    'sensor': 'offers.status_change',
                    'status': 'PASSENGER_CANCELLED',
                },
                'value': 1,
                'timestamp': None,
            },
        ]
    else:
        assert stats == []


@pytest.mark.mongodb_collections('rida_offers')
@pytest.mark.filldb()
async def test_user_offer_create(
        web_app, web_app_client, get_stats_by_label_values, stq,
):
    headers = helpers.get_auth_headers(user_id=3456)
    await helpers.create_offer(web_app_client, headers)
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'offers.status_change'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {'sensor': 'offers.status_change', 'status': 'PENDING'},
            'value': 1,
            'timestamp': None,
        },
    ]
    queue = stq.rida_send_notifications
    task = queue.next_call()
    assert task['kwargs'] == {
        'intent': 'new_offer',
        'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5K',
        'user_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5J',
        'start_point': [53.532, 56.354],
        'point_a': 'point_a',
        'point_b': 'point_b',
        'initial_price': 35.5,
        'currency': 'NGN',
    }

    await helpers.create_offer(
        web_app_client,
        headers,
        expected_response_status=409,
        offer_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5L',
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.translations(
    rida={
        'errors.validation.offer.unexpected_error.title': {
            'en': 'unexpected_error.title',
        },
        'errors.validation.offer.unexpected_error.body': {
            'en': 'unexpected_error.body',
        },
        'errors.validation.offer.unexpected_error.button': {
            'en': 'unexpected_error.button',
        },
        'errors.validation.offer.min_price.title': {'en': 'min_price.title'},
        'errors.validation.offer.min_price.body': {'en': 'min_price.body'},
        'errors.validation.offer.min_price.button': {
            'en': 'min_price.button {suggested_price} {currency}',
        },
        'errors.validation.offer.max_price.title': {'en': 'max_price.title'},
        'errors.validation.offer.max_price.body': {'en': 'max_price.body'},
        'errors.validation.offer.max_price.button': {
            'en': 'max_price.button {suggested_price} {currency}',
        },
    },
)
@pytest.mark.parametrize(
    [
        'expected_status',
        'is_google_maps_error',
        'expected_response',
        'expected_metric',
    ],
    [
        pytest.param(
            200,
            False,
            None,
            consts.PriceValidationResult.IS_VALID,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS,
            ),
            id='no_price_restrictions',
        ),
        pytest.param(
            200,
            False,
            None,
            consts.PriceValidationResult.IS_VALID,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, offer_min_value=15,
            ),
            id='valid_price',
        ),
        pytest.param(
            418,
            False,
            {
                'title': 'min_price.title',
                'body': 'min_price.body',
                'button': 'min_price.button 300 NGN',
                'type': 2,
                'data': {'suggested_price': 300},
            },
            consts.PriceValidationResult.IS_BELOW_MIN_PRICE,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, offer_min_value=300,
            ),
            id='min_price_restriction',
        ),
        pytest.param(
            418,
            False,
            {
                'title': 'max_price.title',
                'body': 'max_price.body',
                'button': 'max_price.button 200 NGN',
                'type': 2,
                'data': {'suggested_price': 200},
            },
            consts.PriceValidationResult.IS_ABOVE_MAX_PRICE,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, offer_max_value=200,
            ),
            id='max_price_restriction',
        ),
        pytest.param(
            418,
            False,
            {
                'title': 'min_price.title',
                'body': 'min_price.body',
                'button': 'min_price.button 300 NGN',
                'type': 2,
                'data': {'suggested_price': 300},
            },
            consts.PriceValidationResult.IS_BELOW_MIN_PERCENT,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, offer_min_percent=1.1,
            ),
            id='min_percent_restriction',
        ),
        pytest.param(
            418,
            False,
            {
                'title': 'max_price.title',
                'body': 'max_price.body',
                'button': 'max_price.button 200 NGN',
                'type': 2,
                'data': {'suggested_price': 200},
            },
            consts.PriceValidationResult.IS_ABOVE_MAX_PERCENT,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, offer_max_percent=0.9,
            ),
            id='max_percent_restriction',
        ),
        pytest.param(
            200,
            True,
            None,
            None,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, offer_max_percent=0.9,
            ),
            id='google_maps_error',
        ),
    ],
)
async def test_offer_create_price_validation(
        web_app,
        web_app_client,
        mockserver,
        get_stats_by_label_values,
        expected_status: int,
        expected_metric: Optional[consts.PriceValidationResult],
        is_google_maps_error: bool,
        expected_response: Optional[Dict[str, Any]],
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        if is_google_maps_error:
            raise mockserver.NetworkError()
        return mockserver.make_response(
            status=200, json=maps_utils.make_gmaps_distance_response(1000, 60),
        )

    headers = helpers.get_auth_headers(user_id=3456)
    response = await helpers.create_offer(
        web_app_client,
        headers,
        expected_response_status=expected_status,
        initial_price=240,
        zone_id=1,
        country_id=12,
    )
    if expected_response is not None:
        response_body = await response.json()
        assert response_body == expected_response
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'price_validation_result'},
    )
    if expected_metric is None:
        assert stats == []
    else:
        assert len(stats) == 1
        metric = stats[0]
        assert metric['kind'] == 'DGAUGE'
        assert metric['value'] == 1.0
        assert metric['labels'] == {
            'sensor': 'price_validation_result',
            'target': 'offer',
            'country_id': '12',
            'zone_id': '1',
            'result': expected_metric.value,
        }

    maps_utils.validate_gmaps_request(
        _mock_google_maps,
        is_google_maps_error is not None,
        [53.532, 56.354],
        [56.322, 34.432],
        _NOW,
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    ['expected_suggested_price'],
    [
        pytest.param(
            20,
            marks=experiments_utils.get_price_overrides_marks(
                user_guid=USER_GUID, time_coefficient=20,
            ),
            id='time_coefficient',
        ),
        pytest.param(
            3,
            marks=experiments_utils.get_price_overrides_marks(
                user_guid=USER_GUID, distance_coefficient=3,
            ),
            id='distance_coefficient',
        ),
        pytest.param(
            1377,
            marks=experiments_utils.get_price_overrides_marks(
                user_guid=USER_GUID, suggest_price_constant=1377,
            ),
            id='suggest_price_constant',
        ),
        pytest.param(
            1477,
            marks=experiments_utils.get_price_overrides_marks(
                user_guid=USER_GUID, min_offer_amount=1477,
            ),
            id='min_offer_amount',
        ),
    ],
)
async def test_offer_create_price_overrides(
        web_app_client, mockserver, mongodb, expected_suggested_price: float,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200, json=maps_utils.make_gmaps_distance_response(1000, 60),
        )

    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5K'
    headers = helpers.get_auth_headers(user_id=3456)
    await helpers.create_offer(
        web_app_client, headers, initial_price=10, zone_id=1, country_id=12,
    )
    offer = mongodb.rida_offers.find_one({'offer_guid': offer_guid})
    assert offer['suggested_price'] == expected_suggested_price

    maps_utils.validate_gmaps_request(
        _mock_google_maps, False, [53.532, 56.354], [56.322, 34.432], _NOW,
    )


@pytest.mark.parametrize(
    'expected_phone',
    [
        pytest.param('msisdn5678     ', id='no rules'),
        pytest.param(
            '+msisdn5678     ',
            id='rule with prefix',
            marks=pytest.mark.config(
                RIDA_PHONE_PREFIX_RULES={
                    'rules': {'android': {'prefix': '+'}},
                },
            ),
        ),
    ],
)
async def test_user_offer_info_driver_phone(
        taxi_rida_web, expected_phone: str,
):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/user/offer/info',
        headers=headers,
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    assert offer['driver']['driver_msisdn'] == expected_phone
