import pytest

from tests_eats_coupons import conftest

PATH = '/v1/couponcheck'
EXTERNAL_META = {'la-la-la': 'ol-ol-ol', 'business_type': 'kakashka'}
DEFAULT_REQUEST = {
    'application': {'name': 'iphone', 'platform_version': [0], 'version': [0]},
    'code': 'unclefuckersqvwsqsyh',
    'country': 'rus',
    'current_yandex_uid': '4063521018',
    'format_currency': False,
    'locale': 'ru',
    'payload': {},
    'payment_info': {'type': 'cash'},
    'payment_options': ['coupon'],
    'service': 'eats',
    'time_zone': 'Europe/Moscow',
    'user_ip': '',
    'zone_classes': [],
    'zone_name': 'moscow',
}


def mock_coupons(request):
    assert request.json == {
        'application': DEFAULT_REQUEST['application'],
        'device_id': '',
        'code': DEFAULT_REQUEST['code'],
        'country': DEFAULT_REQUEST['country'],
        'current_yandex_uid': DEFAULT_REQUEST['current_yandex_uid'],
        'format_currency': DEFAULT_REQUEST['format_currency'],
        'locale': DEFAULT_REQUEST['locale'],
        'payload': DEFAULT_REQUEST['payload'],
        'payment_info': DEFAULT_REQUEST['payment_info'],
        'payment_options': DEFAULT_REQUEST['payment_options'],
        'service': DEFAULT_REQUEST['service'],
        'time_zone': DEFAULT_REQUEST['time_zone'],
        'user_ip': DEFAULT_REQUEST['user_ip'],
        'zone_classes': DEFAULT_REQUEST['zone_classes'],
        'zone_name': DEFAULT_REQUEST['zone_name'],
    }
    return {
        'valid': True,
        'value': 300,
        'format_currency': False,
        'currency_code': 'belka',
        'descr': 'wow',
        'series_purpose': 'support',
        'series_meta': EXTERNAL_META,
        'expire_at': '2020-01-01T01:00:00+00:00',
    }


async def test_request_parsing(taxi_eats_coupons, mockserver):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        return mock_coupons(request)

    expected_status_code = 200
    response = await taxi_eats_coupons.post(
        PATH, json=DEFAULT_REQUEST, headers=conftest.HEADERS,
    )
    assert response.status_code == expected_status_code
    assert response.json() == {
        'valid': True,
        'value': 300,
        'format_currency': False,
        'currency_code': 'belka',
        'descr': 'wow',
        'series_purpose': 'support',
        'series_meta': EXTERNAL_META,
        'business_type': EXTERNAL_META['business_type'],
        'expire_at': '2020-01-01T01:00:00+00:00',
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
