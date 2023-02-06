import copy

import pytest

from tests_eats_coupons import conftest

PATH = '/v1/couponreserve'
EXTERNAL_META = {'la-la-la': 'ol-ol-ol', 'business_type': 'kakashka'}
DEFAULT_REQUEST = {
    'application': {
        'name': 'iphone',
        'platform_version': [1, 2, 3],
        'version': [3, 9, 6],
    },
    'check_type': 'short',
    'code': 'r_coupon_code',
    'country': 'r_country',
    'current_yandex_uid': 'r_yandex_uid',
    'locale': 'rus',
    'order_id': 'r_order_id',
    'payment_info': {
        'method_id': 'card-xc22e3d82b85c9f0e8b2e2e7b',
        'type': 'card',
    },
    'payment_options': ['coupon'],
    'region_id': 213,
    'service': 'eats',
    'time_zone': 'Europe/Moscow',
    'user_ip': '172.27.219.189',
    'zone_classes': [],
    'zone_name': 'moscow',
}


async def test_request_parsing_timeout(taxi_eats_coupons, mockserver):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        raise mockserver.TimeoutError()

    expected_status_code = 408
    response = await taxi_eats_coupons.post(
        PATH, json=DEFAULT_REQUEST, headers=conftest.HEADERS,
    )
    assert response.status_code == expected_status_code


async def test_request_parsing_network(taxi_eats_coupons, mockserver):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        raise mockserver.NetworkError()

    expected_status_code = 424
    response = await taxi_eats_coupons.post(
        PATH, json=DEFAULT_REQUEST, headers=conftest.HEADERS,
    )
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    'payload, exp_payload',
    [
        pytest.param(
            None,
            {'card_id': 'card-xc22e3d82b85c9f0e8b2e2e7b'},
            id='empty_payload',
        ),
        pytest.param(
            {'place_id': 'some_place'},
            {
                'place_id': 'some_place',
                'card_id': 'card-xc22e3d82b85c9f0e8b2e2e7b',
            },
            id='some_payload',
        ),
    ],
)
async def test_request_parsing(
        taxi_eats_coupons, mockserver, payload, exp_payload,
):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        exp_request = copy.deepcopy(DEFAULT_REQUEST)
        exp_request['payload'] = exp_payload
        return mock_coupons(request, exp_request)

    expected_status_code = 200
    request = copy.deepcopy(DEFAULT_REQUEST)
    if payload:
        request['payload'] = payload

    response = await taxi_eats_coupons.post(
        PATH, json=request, headers=conftest.HEADERS,
    )
    assert response.status_code == expected_status_code
    assert response.json() == {
        'exists': True,
        'valid': True,
        'valid_any': False,
        'value': 0.0,
        'series': 'r_series',
        'business_type': EXTERNAL_META['business_type'],
        'expire_at': '2020-01-01T01:00:00+00:00',
        'currency_code': 'RUB',
        'error_code': 'ERROR_CODE',
        'descr': 'error description',
    }


async def test_unauthorized_request(taxi_eats_coupons, mockserver):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        exp_request = copy.deepcopy(DEFAULT_REQUEST)
        return mock_coupons(request, exp_request)

    expected_status_code = 401
    response = await taxi_eats_coupons.post(PATH, json=DEFAULT_REQUEST)
    assert response.status_code == expected_status_code


def format_order_id(order_id):
    return 'eats:{' + order_id + '}'


def mock_coupons(request, exp_request):
    assert request.json == {
        'application': exp_request['application'],
        'check_type': exp_request['check_type'],
        'code': exp_request['code'],
        'country': exp_request['country'],
        'current_yandex_uid': exp_request['current_yandex_uid'],
        'device_id': '',
        'locale': exp_request['locale'],
        'order_id': format_order_id(exp_request['order_id']),
        'payload': exp_request['payload'],
        'payment_info': exp_request['payment_info'],
        'payment_options': exp_request['payment_options'],
        'region_id': exp_request['region_id'],
        'service': exp_request['service'],
        'time_zone': exp_request['time_zone'],
        'user_ip': exp_request['user_ip'],
        'zone_classes': exp_request['zone_classes'],
        'zone_name': exp_request['zone_name'],
    }
    return {
        'exists': True,
        'valid': True,
        'valid_any': False,
        'value': 0.0,
        'series': 'r_series',
        'series_meta': EXTERNAL_META,
        'expire_at': '2020-01-01T01:00:00+00:00',
        'currency_code': 'RUB',
        'error_code': 'ERROR_CODE',
        'descr': 'error description',
    }


@pytest.mark.parametrize('taxi_coupons_response', [400, 429])
async def test_response_proxy(
        taxi_eats_coupons,
        mockserver,
        mock_coupons_response_proxy,
        response_context,
        taxi_coupons_response,
):
    response_context.set_params(
        conftest.ResponseParams(code=taxi_coupons_response),
    )

    response = await taxi_eats_coupons.post(
        PATH, json=DEFAULT_REQUEST, headers=conftest.HEADERS,
    )
    assert response.status_code == taxi_coupons_response
