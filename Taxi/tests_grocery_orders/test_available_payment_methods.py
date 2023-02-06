import pytest


from . import headers

MERCHANT_ID_LIST = ['value1', 'value2', 'value3']
SERVICE = 'grocery'
LOCATION = [37.62, 55.75]

CARD: dict = {
    'availability': {'available': True, 'disabled_reason': ''},
    'bin': '462729',
    'currency': 'RUB',
    'id': 'card-x3609',
    'name': 'VISA',
    'number': '462729****0957',
    'system': 'VISA',
    'type': 'card',
}
API_PROXY_CARD = {**CARD, 'available': True}

API_PROXY_APPLE_PAY = {'type': 'applepay'}
APPLE_PAY = {
    'type': 'applepay',
    'availability': {'available': True, 'disabled_reason': ''},
}

API_PROXY_GOOGLE_PAY = {'type': 'googlepay'}
GOOGLE_PAY = {
    'type': 'googlepay',
    'availability': {'available': True, 'disabled_reason': ''},
}

BADGE = {
    'availability': {'available': True, 'disabled_reason': ''},
    'currency': 'RUB',
    'description': 'оплата бейджиком',
    'id': 'badge:yandex_badge:RUB',
    'name': 'Yandex Badge',
    'type': 'corp',
}

CORP = {
    'availability': {'available': True, 'disabled_reason': ''},
    'currency': 'RUB',
    'description': 'eats 3796 of 10000 RUB',
    'id': 'corp:9e63c266c0d84206bbc8765f2cf7a730:RUB',
    'name': 'corp-test',
    'type': 'corp',
}

ALL_API_PROXY_PAYMENT_METHODS = [
    API_PROXY_CARD,
    API_PROXY_APPLE_PAY,
    API_PROXY_GOOGLE_PAY,
    BADGE,
    CORP,
]

ALL_PAYMENT_METHODS = [CARD, APPLE_PAY, GOOGLE_PAY, BADGE, CORP]


@pytest.fixture(name='api_proxy_mock')
def mock_api_proxy(mockserver):
    def _mock_api_proxy():
        @mockserver.json_handler(
            '/api-proxy-superapp-critical'
            '/4.0/payments/v1/list-payment-methods',
        )
        def _mock(request):
            assert request.json == {'location': LOCATION}

            return {
                'merchant_id_list': MERCHANT_ID_LIST,
                'payment_methods': ALL_API_PROXY_PAYMENT_METHODS,
                'last_used_payment_method': {
                    'id': 'badge:yandex_badge:RUB',
                    'type': 'corp',
                },
            }

        return _mock

    return _mock_api_proxy


async def test_available_payment_methods(taxi_grocery_orders, api_proxy_mock):
    api_proxy = api_proxy_mock()

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/available-payment-methods',
        json={'location': [37.62, 55.75]},
        params={'service': SERVICE},
        headers=headers.DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    assert api_proxy.times_called == 1
    assert response.json() == {
        'last_used_payment_method': {
            'id': 'badge:yandex_badge:RUB',
            'type': 'corp',
        },
        'merchant_id_list': MERCHANT_ID_LIST,
        'payment_methods': ALL_PAYMENT_METHODS,
    }
