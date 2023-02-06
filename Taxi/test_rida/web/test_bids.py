import datetime
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from rida import consts
from rida.repositories.mongo import bid as bid_repository
from test_rida import experiments_utils
from test_rida import helpers
from test_rida import maps_utils


_NOW = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)


@pytest.mark.mongodb_collections('rida_bids')
@pytest.mark.filldb()
@pytest.mark.parametrize(
    ['bid_guid', 'expected_status'],
    [
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A', 200, id='happy_path',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFAAAAA', 409, id='not_found',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5T', 409, id='incorrect_state',
        ),
    ],
)
async def test_user_bid_accept(
        web_app,
        web_app_client,
        get_stats_by_label_values,
        bid_guid,
        expected_status,
):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await web_app_client.post(
        '/v3/user/bid/accept', headers=headers, json={'bid_guid': bid_guid},
    )
    assert response.status == expected_status
    if expected_status == 200:
        stats = get_stats_by_label_values(
            web_app['context'], {'sensor': 'offers.status_change'},
        )
        assert stats == [
            {
                'kind': 'IGAUGE',
                'labels': {
                    'sensor': 'offers.status_change',
                    'status': 'DRIVING',
                },
                'value': 1,
                'timestamp': None,
            },
        ]


@pytest.mark.mongodb_collections('rida_bids')
@pytest.mark.filldb()
@pytest.mark.parametrize(
    ['bid_guid', 'expected_status'],
    [
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A', 200, id='happy_path',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFAAAAA', 400, id='not_found',
        ),
    ],
)
async def test_user_bid_decline(
        taxi_rida_web, bid_guid: str, expected_status: int,
):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/user/bid/decline', headers=headers, json={'bid_guid': bid_guid},
    )
    assert response.status == expected_status

    response = await taxi_rida_web.post(
        '/v3/user/bid/decline', headers=headers, json={'bid_guid': bid_guid},
    )
    assert response.status == expected_status


@pytest.mark.mongodb_collections('rida_bids')
@pytest.mark.filldb()
async def test_driver_bid_cancel(taxi_rida_web):
    headers = helpers.get_auth_headers(user_id=5678)
    response = await taxi_rida_web.post(
        '/v3/driver/bid/cancel',
        headers=headers,
        json={'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    assert response.status == 200

    response = await taxi_rida_web.post(
        '/v3/driver/bid/cancel',
        headers=headers,
        json={'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    assert response.status == 200


@pytest.mark.mongodb_collections('rida_bids', 'rida_drivers')
@pytest.mark.filldb()
@pytest.mark.now('2025-04-29T12:12:00.000+0000')
async def test_driver_bid_place(web_app, web_app_client, stq, mongodb):
    bid_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'
    # bid already exists, remove them
    mongodb.rida_bids.remove({'bid_guid': bid_guid})
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'
    headers = helpers.get_auth_headers(user_id=5678)
    response = await web_app_client.post(
        '/v3/driver/bid/place',
        headers=headers,
        json={
            'bid_guid': bid_guid,
            'offer_guid': offer_guid,
            'proposed_price': 500,
        },
    )
    assert response.status == 200
    data = (await response.json())['data']
    assert data['bid_guid'] == bid_guid

    stq_calls_kwargs = []
    for _ in range(3):
        stq_call_kwargs = stq.rida_send_notifications.next_call()['kwargs']
        stq_calls_kwargs.append(stq_call_kwargs)
    stq_calls_kwargs.sort(key=lambda stq_call: stq_call['intent'])
    assert stq_calls_kwargs[0] == {
        'intent': 'add_bid',
        'user_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        'price': 500,
        'currency': 'NGN',
    }

    # it works with the same bid_guid
    response = await web_app_client.post(
        '/v3/driver/bid/place',
        headers=headers,
        json={
            'bid_guid': bid_guid,
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            'proposed_price': 500,
        },
    )
    assert response.status == 200
    data = (await response.json())['data']
    assert data['bid_guid'] == bid_guid

    bid_repo: bid_repository.BidRepository = web_app['context'].bid_repo
    bid = await bid_repo.find_one(bid_guid)
    assert bid['bid_status_log'][0]['log_id'] == 'new_status.PENDING'


@pytest.mark.mongodb_collections('rida_bids', 'rida_drivers')
@pytest.mark.filldb()
@pytest.mark.now('2025-04-29T12:12:00.000+0000')
async def test_driver_bid_place_prolong(taxi_rida_web, mongodb):
    mongodb.rida_bids.remove(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    response = await taxi_rida_web.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    assert 'expired_after' in offer
    assert offer['expired_after'] == 14

    doc = mongodb.rida_offers.find_one(
        {'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
        {'expired_at': 1},
    )
    headers = helpers.get_auth_headers(user_id=5678)
    response = await taxi_rida_web.post(
        '/v3/driver/bid/place',
        headers=headers,
        json={
            'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            'proposed_price': 500,
        },
    )
    assert response.status == 200
    new_doc = mongodb.rida_offers.find_one(
        {'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
        {'expired_at': 1},
    )
    diff = new_doc['expired_at'] - doc['expired_at']
    assert diff == datetime.timedelta(seconds=60)

    response = await taxi_rida_web.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    assert 'expired_after' in offer
    assert offer['expired_after'] == 74


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.mongodb_collections('rida_bids', 'rida_drivers')
@pytest.mark.filldb()
@pytest.mark.parametrize(
    ['error', 'extected_eta_seconds'],
    [
        pytest.param(None, 100, id='happy_path'),
        # NOTE: Erros do not support. Waiting for TAXIDATA-1455
        pytest.param('network', None, id='network_error'),
        pytest.param('timeout', None, id='timeout_error'),
    ],
)
@pytest.mark.config(RIDA_FETCH_ETA_IN_BID_PLACE_ENABLED=True)
async def test_driver_bid_place_fetch_eta(
        web_app_client, mockserver, mongodb, error, extected_eta_seconds,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        if error == 'network':
            raise mockserver.NetworkError()
        elif error == 'timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(
                200, extected_eta_seconds,
            ),
        )

    mongodb.rida_bids.remove(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    headers = helpers.get_auth_headers(user_id=5678)
    response = await web_app_client.post(
        '/v3/driver/bid/place',
        headers=headers,
        json={
            'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            'proposed_price': 500,
        },
    )
    assert response.status == 200

    bid_doc = mongodb.rida_bids.find_one(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    if error is None:
        assert bid_doc['eta_seconds'] == 100
    else:
        assert bid_doc['eta_seconds'] is None

    maps_utils.validate_gmaps_request(
        _mock_google_maps,
        error is not None,
        [44.5288845, 40.2104517],
        [44.580257, 40.2185829],
        _NOW,
    )


PRICE_VALIDATION_EXP_ARGS = experiments_utils.PriceValidationSettingsExpArgs(
    country_id=2,
    zone_id=0,
    is_driver=True,
    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
    device_uuid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
)


@pytest.mark.translations(
    rida={
        'errors.validation.bid.min_price.title': {'en': 'min_price.title'},
        'errors.validation.bid.min_price.body': {'en': 'min_price.body'},
        'errors.validation.bid.min_price.button': {
            'en': '{suggested_price} {currency} min_price.button',
        },
        'errors.validation.bid.max_price.title': {'en': 'max_price.title'},
        'errors.validation.bid.max_price.body': {'en': 'max_price.body'},
        'errors.validation.bid.max_price.button': {
            'en': '{suggested_price} {currency} max_price.button',
        },
    },
)
@pytest.mark.parametrize(
    ['expected_status', 'expected_response', 'expected_metric'],
    [
        pytest.param(
            200,
            None,
            consts.PriceValidationResult.IS_VALID,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS,
            ),
            id='no_price_restrictions',
        ),
        pytest.param(
            200,
            None,
            consts.PriceValidationResult.IS_VALID,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, bid_min_value=15,
            ),
            id='valid_price',
        ),
        pytest.param(
            418,
            {
                'title': 'min_price.title',
                'body': 'min_price.body',
                'button': '600 NGN min_price.button',
                'type': 2,
                'data': {'suggested_price': 600},
            },
            consts.PriceValidationResult.IS_BELOW_MIN_PRICE,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, bid_min_value=600,
            ),
            id='min_price_restriction',
        ),
        pytest.param(
            418,
            {
                'title': 'max_price.title',
                'body': 'max_price.body',
                'button': '400 NGN max_price.button',
                'type': 2,
                'data': {'suggested_price': 400},
            },
            consts.PriceValidationResult.IS_ABOVE_MAX_PRICE,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, bid_max_value=400,
            ),
            id='max_price_restriction',
        ),
        pytest.param(
            418,
            {
                'title': 'min_price.title',
                'body': 'min_price.body',
                'button': '1200 NGN min_price.button',
                'type': 2,
                'data': {'suggested_price': 1200},
            },
            consts.PriceValidationResult.IS_BELOW_MIN_PERCENT,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, bid_min_percent=1.1,
            ),
            id='min_percent_restriction',
        ),
        pytest.param(
            200,
            None,
            consts.PriceValidationResult.IS_VALID,
            # 1111.79 * 0.49 = 544 ~ 500
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, bid_min_percent=0.49,
            ),
            id='min_percent_restriction_rounding_down',
        ),
        pytest.param(
            418,
            {
                'title': 'max_price.title',
                'body': 'max_price.body',
                'button': '300 NGN max_price.button',
                'type': 2,
                'data': {'suggested_price': 300},
            },
            consts.PriceValidationResult.IS_ABOVE_MAX_PERCENT,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS, bid_max_percent=0.3,
            ),
            id='max_percent_restriction',
        ),
    ],
)
async def test_bid_place_price_validation(
        web_app,
        web_app_client,
        mongodb,
        get_stats_by_label_values,
        expected_status: int,
        expected_response: Optional[Dict[str, Any]],
        expected_metric: Optional[consts.PriceValidationResult],
):
    # bid already exists, remove them
    mongodb.rida_bids.remove(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    response = await web_app_client.post(
        '/v3/driver/bid/place',
        headers=helpers.get_auth_headers(user_id=5678),
        json={
            'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            'proposed_price': 500,
        },
    )
    assert response.status == expected_status
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
        assert metric['value'] == 0.4498061335564372
        assert metric['labels'] == {
            'sensor': 'price_validation_result',
            'target': 'bid',
            'country_id': '2',
            'zone_id': '0',
            'result': expected_metric.value,
        }


@pytest.mark.parametrize(
    ['expected_ttl'],
    [
        pytest.param(60, id='config_value'),
        pytest.param(
            90,
            marks=[
                pytest.mark.client_experiments3(
                    consumer='rida',
                    experiment_name='rida_bid_ttl',
                    args=[
                        {
                            'name': 'user_guid',
                            'type': 'string',
                            'value': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                        },
                        {'name': 'country_id', 'type': 'int', 'value': 2},
                        {'name': 'zone_id', 'type': 'int', 'value': 0},
                    ],
                    value={'bid_ttl': 90},
                ),
            ],
            id='experiment_value',
        ),
    ],
)
async def test_bid_ttl_exp(web_app_client, mongodb, expected_ttl: int):
    # bid already exists, remove them
    mongodb.rida_bids.remove(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    response = await web_app_client.post(
        '/v3/driver/bid/place',
        headers=helpers.get_auth_headers(user_id=5678),
        json={
            'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            'proposed_price': 500,
        },
    )
    assert response.status == 200
    bid = mongodb.rida_bids.find_one(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    ttl = bid['expired_at'] - bid['created_at']
    assert ttl == datetime.timedelta(seconds=expected_ttl)


def _eta_source(source: str):
    return pytest.mark.config(RIDA_BID_ETA_SOURCE_2=source)


@experiments_utils.get_distance_info_config(
    'mapbox',
    'v3/driver/bid/place',
    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
)
@pytest.mark.parametrize(
    'eta_from_client, eta_expected, should_call_router',
    [
        pytest.param(0, 0, False, marks=[_eta_source('client')]),
        pytest.param(50, 50, False, marks=[_eta_source('client')]),
        pytest.param(
            0, 45, True, marks=[_eta_source('router_if_client_eta_is_zero')],
        ),
        pytest.param(
            50, 50, False, marks=[_eta_source('router_if_client_eta_is_zero')],
        ),
        pytest.param(0, 45, True, marks=[_eta_source('router')]),
        pytest.param(50, 45, True, marks=[_eta_source('router')]),
    ],
)
async def test_bid_zero_ttl(
        web_app_client,
        mongodb,
        eta_from_client,
        eta_expected,
        should_call_router,
        mockserver,
):
    # bid already exists, remove them
    mongodb.rida_bids.remove(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )

    @mockserver.json_handler('/api-proxy-external-geo/directions/v5/mapbox')
    def _mock_maps(request):
        return maps_utils.make_mapbox_directions_response(
            [], 45, 228, 200, 'Ok', False, mockserver,
        )

    response = await web_app_client.post(
        '/v3/driver/bid/place',
        headers=helpers.get_auth_headers(user_id=5678),
        json={
            'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A',
            'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D',
            'proposed_price': 500,
            'eta_seconds': eta_from_client,
        },
    )
    assert response.status == 200
    bid = mongodb.rida_bids.find_one(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
    )
    assert bid['eta_seconds'] == eta_expected
    assert _mock_maps.has_calls == should_call_router


@pytest.mark.parametrize(
    'new_bid_status',
    [
        consts.BidStatus.ACCEPTED,
        consts.BidStatus.DECLINED,
        consts.BidStatus.PASSENGER_CANCELED,
        consts.BidStatus.ACCEPTED_ANOTHER_DRIVER,
    ],
)
async def test_bid_status_log(web_app, new_bid_status: consts.BidStatus):
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'
    price_sequence = 1
    bid_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'
    bid_repo: bid_repository.BidRepository = web_app['context'].bid_repo

    if new_bid_status == consts.BidStatus.ACCEPTED:
        await bid_repo.accept(bid_guid)
    elif new_bid_status == consts.BidStatus.DECLINED:
        await bid_repo.decline(bid_guid)
    elif new_bid_status == consts.BidStatus.PASSENGER_CANCELED:
        await bid_repo.passenger_cancel(offer_guid, price_sequence)
    elif new_bid_status == consts.BidStatus.ACCEPTED_ANOTHER_DRIVER:
        await bid_repo.accept_another_driver(offer_guid, price_sequence)
    else:
        raise ValueError(f'Unexpected new bid status {new_bid_status}')

    bid = await bid_repo.find_one(bid_guid)
    assert bid is not None
    assert bid['bid_status'] == new_bid_status.value
    assert 'bid_status_log' in bid
    bid_status_log = bid['bid_status_log']
    assert len(bid_status_log) > 0  # pylint: disable=len-as-condition
    last_log = bid_status_log[-1]
    assert last_log['log_id'] == f'new_status.{new_bid_status.value}'


async def test_duplicate_bids(web_app_client):
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5D'},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    assert len(offer['bids']) == 2  # one for each driver, excluding dupes
