import pytest

from . import consts
from . import headers
from .plugins import configs
from .plugins import mock_api_proxy

CARD = {
    'availability': {'available': True, 'disabled_reason': ''},
    'bin': '462729',
    'currency': 'RUB',
    'id': 'card-x3609',
    'name': 'VISA',
    'number': '462729****0957',
    'system': 'VISA',
    'type': 'card',
}

APPLE_PAY = {
    'availability': {'available': True, 'disabled_reason': ''},
    'name': 'Apple pay RUS',
    'type': 'applepay',
}

GOOGLE_PAY = {
    'availability': {'available': True, 'disabled_reason': ''},
    'name': 'Google pay RUS',
    'type': 'googlepay',
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

CIBUS = {
    'availability': {'available': True, 'disabled_reason': ''},
    'name': 'Cibus RUS',
    'type': 'cibus',
}

SBP = {
    'availability': {'available': True, 'disabled_reason': ''},
    'name': 'SBP RUS',
    'type': 'sbp',
    'id': 'sbp_qr',
}


@pytest.fixture(name='grocery_available_payment_methods')
def _grocery_available_payment_methods(taxi_grocery_payments, api_proxy):
    async def _inner(status_code=200, extra_headers=None):
        response = await taxi_grocery_payments.post(
            '/lavka/v1/payments/v1/available-payment-methods',
            json={'location': mock_api_proxy.LOCATION},
            headers={**headers.DEFAULT_HEADERS, **(extra_headers or {})},
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


async def test_available_payment_methods(
        grocery_available_payment_methods, api_proxy,
):
    response = await grocery_available_payment_methods()

    assert api_proxy.lpm_times_called() == 1
    assert response == {
        'last_used_payment_method': {
            'id': 'badge:yandex_badge:RUB',
            'type': 'corp',
        },
        'merchant_id_list': mock_api_proxy.MERCHANT_ID_LIST,
        'payment_methods': [
            CARD,
            APPLE_PAY,
            GOOGLE_PAY,
            BADGE,
            CORP,
            CIBUS,
            SBP,
        ],
    }


@pytest.mark.parametrize(
    'locale, locale_suffix', [('ru', 'RUS'), ('en', 'EN'), ('unknown', 'EN')],
)
async def test_other_payments_name(
        grocery_available_payment_methods, locale, locale_suffix,
):
    response = await grocery_available_payment_methods(
        extra_headers={'X-Request-Language': locale},
    )

    payment_types = {
        'applepay': 'Apple pay',
        'googlepay': 'Google pay',
        'cibus': 'Cibus',
        'sbp': 'SBP',
    }

    def _get_name(payment_type):
        for payment_method in response['payment_methods']:
            if payment_method['type'] == payment_type:
                return payment_method['name']
        return None

    for payment_type, payment_name in payment_types.items():
        assert _get_name(payment_type) == f'{payment_name} {locale_suffix}'


@pytest.mark.parametrize('drop_unavailable_payment_methods', [True, False])
async def test_drop_unavailable_payment_methods(
        grocery_available_payment_methods,
        grocery_payments_configs,
        api_proxy,
        drop_unavailable_payment_methods,
):
    grocery_payments_configs.drop_unavailable_payment_methods(
        enabled=drop_unavailable_payment_methods,
    )

    api_proxy.card_data['availability']['available'] = False
    api_proxy.badge_data['availability']['available'] = False
    api_proxy.corp_data['availability']['available'] = False

    response = await grocery_available_payment_methods()

    has_unavailable_methods = False
    for payment_method in response['payment_methods']:
        if not payment_method['availability']['available']:
            has_unavailable_methods = True
            break

    assert drop_unavailable_payment_methods != has_unavailable_methods


@configs.GROCERY_MERCHANTS
@pytest.mark.parametrize(
    'app_name, merchant_ids',
    [
        (headers.ANDROID_APP_NAME, [consts.MERCHANT_ANDROID]),
        (headers.IPHONE_APP_NAME, [consts.MERCHANT_IPHONE]),
        ('some-trash', mock_api_proxy.MERCHANT_ID_LIST),
    ],
)
async def test_merchant_ids(
        grocery_available_payment_methods, app_name, merchant_ids,
):
    response = await grocery_available_payment_methods(
        extra_headers={'X-Request-Application': f'app_name={app_name}'},
    )

    assert response['merchant_id_list'] == merchant_ids
