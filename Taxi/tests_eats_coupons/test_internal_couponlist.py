import typing

import pytest

from tests_eats_coupons import conftest

PATH = '/internal/couponlist'

DEFAULT_REQUEST: typing.Dict = dict()


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
        'promocodes': [
            {
                'code': 'r_code1',
                'currency': {'code': 'r_currency_code1', 'sign': '₽'},
                'discount': 10,
                'is_used': False,
                'percentage': True,
                'status': 'invalid',
                'business_type': 'place_discount',
                'expired_at': '2021-05-20T00:00:00+00:00',
            },
            {
                'code': 'r_code2',
                'currency': {'code': 'r_currency_code2', 'sign': '₽'},
                'discount': 100,
                'is_used': False,
                'percentage': False,
                'status': 'invalid',
                'business_type': 'discount',
                'expired_at': '2021-05-20T00:00:00+00:00',
            },
        ],
    }


async def test_request_without_passport(taxi_eats_coupons, mockserver):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        assert False

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        assert False

    expected_status_code = 400
    response = await taxi_eats_coupons.post(
        PATH, json=DEFAULT_REQUEST, headers=conftest.HEADERS_PASSPRT_EMPTY,
    )
    assert response.status_code == expected_status_code


async def test_unauthorized_request(taxi_eats_coupons, mockserver):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        return mock_coupons(request)

    expected_status_code = 401
    response = await taxi_eats_coupons.post(PATH, json=DEFAULT_REQUEST)
    assert response.status_code == expected_status_code


def format_order_id(order_id):
    return 'eats:{' + order_id + '}'


def mock_coupons(request):
    assert 'country' in request.json
    assert 'payment' in request.json
    assert 'service' in request.json
    assert 'services' in request.json
    assert 'zone_name' in request.json
    return {
        'coupons': [
            {
                'code': 'r_code1',
                'percent': 10,
                'status': 'r_status1',
                'currency_code': 'r_currency_code1',
                'expire_at': conftest.DATETIME,
                'currency_rules': {
                    'code': 'RUB',
                    'text': 'руб.',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'sign': '₽',
                },
                'series_meta': {
                    'description_tanker_key': 'description_key',
                    'business_type': 'place_discount',
                },
            },
            {
                'code': 'r_code2',
                'value': 100,
                'status': 'r_status2',
                'currency_code': 'r_currency_code2',
                'expire_at': conftest.DATETIME_FRACTION,
                'currency_rules': {
                    'code': 'RUB',
                    'text': 'руб.',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'sign': '₽',
                },
                'series_meta': {'description_tanker_key': 'description_key'},
            },
        ],
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


EATS_COUPONS_TRANSLATIONS = {
    'eats_eats-coupons': {'description_key': {'ru': 'some description'}},
}


@pytest.mark.translations(**EATS_COUPONS_TRANSLATIONS)
async def test_translation_200(taxi_eats_coupons, mockserver):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        return mock_coupons(request)

    response = await taxi_eats_coupons.post(
        PATH, json=DEFAULT_REQUEST, headers=conftest.HEADERS,
    )

    assert response.status_code == 200

    for promocode in response.json()['promocodes']:
        assert promocode['description'] == 'some description'
        assert promocode['expired_at'] == conftest.DATETIME


EATS_COUPONS_WRONG_TRANSLATIONS = {
    'eats_eats-coupons': {'description_key_2': {'ru': 'some description'}},
}


@pytest.mark.translations(**EATS_COUPONS_WRONG_TRANSLATIONS)
async def test_not_translation(taxi_eats_coupons, mockserver):
    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        return mock_coupons(request)

    response = await taxi_eats_coupons.post(
        PATH, json=DEFAULT_REQUEST, headers=conftest.HEADERS,
    )

    assert response.status_code == 200

    for promocode in response.json()['promocodes']:
        assert 'description' not in promocode


@pytest.mark.translations(**EATS_COUPONS_TRANSLATIONS)
async def test_description_from_coupon(taxi_eats_coupons, mockserver):
    description = 'Ресторан Большая Кувшинка извиняется'

    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        return {
            'coupons': [
                {
                    'code': 'r_code1',
                    'percent': 10,
                    'status': 'r_status1',
                    'currency_code': 'r_currency_code1',
                    'expire_at': conftest.DATETIME,
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                    'series_meta': {
                        # Не смотря на наличие поля ключа перевода в серии
                        # должен быть выбран перевод из поля description,
                        # если он есть
                        'description_tanker_key': 'description_key',
                    },
                    'description': description,
                },
                {
                    'code': 'r_code2',
                    'percent': 10,
                    'status': 'r_status1',
                    'currency_code': 'r_currency_code1',
                    'expire_at': conftest.DATETIME,
                    'currency_rules': {
                        'code': 'RUB',
                        'text': 'руб.',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'sign': '₽',
                    },
                    'series_meta': {
                        'description_tanker_key': 'description_key',
                    },
                },
            ],
        }

    response = await taxi_eats_coupons.post(
        PATH, json=DEFAULT_REQUEST, headers=conftest.HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['promocodes'][0]['description'] == description
    assert response.json()['promocodes'][1]['description'] != description


@pytest.mark.parametrize(
    'successful', [pytest.param(False), pytest.param(True)],
)
async def test_cart_params_forwarding(
        taxi_eats_coupons, load_json, mockserver, successful,
):
    cart_response = conftest.get_eats_cart_response(load_json)
    cart_id = cart_response['place']['id']

    @mockserver.json_handler('/eats-notifications/v1/get-device')
    def _mock_notifications(request):
        return {}

    @mockserver.json_handler('/coupons' + PATH)
    def _mock_coupons(request):
        if successful:
            assert request.json['payload'].get(
                'shipping_type',
            ) == cart_response.get('shipping_type')
            assert request.json['payload'].get(
                'brand_id',
            ) == cart_response.get('brand_id')
            assert request.json['payload'].get('place_id') == int(
                cart_response.get('place', dict()).get('id'),
            )
            assert request.json['payload'].get('cart_total') == int(
                cart_response.get('total'),
            )

            for item in cart_response['items']:
                place_menu_item = item.get('place_menu_item')
                if place_menu_item:
                    assert (
                        place_menu_item
                        in request.json['payload']['place_menu_items']
                    )
        else:
            assert not request.json['payload']

        return mock_coupons(request)

    @mockserver.json_handler('/eats-cart/internal/eats-cart/v1/get_cart')
    def _mock_eats_cart(request):
        if not successful:
            return mockserver.make_response(status=404)
        assert request.json['cart_id'] == cart_id
        return mockserver.make_response(json=cart_response, status=200)

    expected_status_code = 200
    response = await taxi_eats_coupons.post(
        PATH, json={'cart_id': cart_id}, headers=conftest.HEADERS,
    )

    assert _mock_eats_cart.has_calls
    assert response.status_code == expected_status_code
    assert response.json() == {
        'promocodes': [
            {
                'code': 'r_code1',
                'currency': {'code': 'r_currency_code1', 'sign': '₽'},
                'discount': 10,
                'is_used': False,
                'percentage': True,
                'status': 'invalid',
                'business_type': 'place_discount',
                'expired_at': '2021-05-20T00:00:00+00:00',
            },
            {
                'code': 'r_code2',
                'currency': {'code': 'r_currency_code2', 'sign': '₽'},
                'discount': 100,
                'is_used': False,
                'percentage': False,
                'status': 'invalid',
                'business_type': 'discount',
                'expired_at': '2021-05-20T00:00:00+00:00',
            },
        ],
    }
