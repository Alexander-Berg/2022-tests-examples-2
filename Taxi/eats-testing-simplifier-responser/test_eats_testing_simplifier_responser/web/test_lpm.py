# pylint: disable=too-many-lines
# pylint: disable=invalid-string-quote
# pylint: disable=wildcard-import
# pylint: disable=ungrouped-imports
# pylint: disable=unused-wildcard-import
# pylint: disable=redefined-builtin
# pylint: disable=unused-variable
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=unnecessary-lambda

# pylint: disable=bad-whitespace
# flake8: noqa
import pytest


@pytest.mark.config(
    EATS_TESTING_SIMPLIFIER_RESPONSER_DEFAULT_PAYMENT_METHODS_NEW={
        'default_payment_methods': [
            {
                'availability': {'available': True, 'disabled_reason': ''},
                'bin': '424242',
                'currency': 'RUB',
                'id': 'card-x8e000cd57550021906e9ee43',
                'is_default': True,
                'name': 'VISA',
                'number': '424242****4242',
                'service_token': 'testtoken',
                'system': 'VISA',
                'type': 'card',
                'short_title': '** visa 4242',
            },
            {
                'availability': {
                    'available': False,
                    'disabled_reason': (
                        'Требуется ' 'верификация ' 'на ' 'этом ' 'устройстве'
                    ),
                },
                'bin': '555555',
                'currency': 'RUB',
                'id': 'card-x8e000cd57550021906e9ee44',
                'is_default': True,
                'name': 'MasterCard',
                'number': '555555****4444',
                'service_token': 'testtoken2',
                'system': 'MasterCard',
                'type': 'card',
                'short_title': '** visa 4444',
            },
            {
                'availability': {'available': True, 'disabled_reason': ''},
                'id': 'applepay',
                'is_default': True,
                'merchant_id_list': [
                    'merchant.ru.yandex.ytaxi.trust',
                    'merchant.ru.yandex.mobile.development',
                    'merchant.ru.yandex.taxi.develop',
                ],
                'service_token': 'tokenapple',
                'type': 'applepay',
                'name': 'applepay',
            },
            {
                'availability': {'available': True, 'disabled_reason': ''},
                'id': 'googlepay',
                'is_default': True,
                'merchant_id': 'merchant.ru.yandex.ytaxi.trust',
                'service_token': 'google',
                'type': 'googlepay',
                'name': 'googlepay',
            },
            {
                'availability': {'available': True, 'disabled_reason': ''},
                'binding_service_token': 'add_new_card',
                'id': 'add_new_card',
                'is_default': False,
                'type': 'add_new_card',
                'name': 'add_new_card',
            },
            {
                'availability': {'available': False, 'disabled_reason': ''},
                'id': 'cash',
                'is_default': False,
                'type': 'cash',
                'name': 'cash',
            },
            {
                'availability': {'available': True, 'disabled_reason': ''},
                'id': 'sbp',
                'is_default': True,
                'type': 'sbp',
                'name': 'sbp',
            },
            {
                'availability': {'available': True, 'disabled_reason': ''},
                'currency': 'RUB',
                'description': '',
                'id': 'corp:7c3a629872d944d8b7fad154aff37b14:RUB',
                'is_default': True,
                'name': 'Кабинет для QA Еды',
                'type': 'corp',
                'balance_left': '1000.00',
            },
            {
                'availability': {
                    'available': False,
                    'disabled_reason': 'нужна ' 'подписка ' 'на ' 'Плюс',
                },
                'complement_attributes': {
                    'compatibility_description': 'Работает ' 'с ' 'картой',
                    'name': 'Плюс ' '— ' 'потратить ' 'на ' 'поездку',
                    'payment_types': ['card'],
                },
                'currency_rules': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$\u2006' '$SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
                'description': '1154',
                'id': 'w/031bb88c-2e53-5f95-a2f6-82b6886c61f2',
                'is_complement': True,
                'is_default': True,
                'money_left': '1154',
                'name': 'Плюс',
                'type': 'personal_wallet',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'uid,expected_response_json',
    [
        (
            pytest.param(
                '1',
                {
                    'payment_methods': [
                        {
                            'type': 'googlepay',
                            'name': 'googlepay',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'merchant_id': 'merchant.ru.yandex.ytaxi.trust',
                            'service_token': 'google',
                        },
                    ],
                    'region_id': 51,
                    'last_used_payment_method': {
                        'id': 'googlepay',
                        'type': 'googlepay',
                    },
                },
                id='uid in DB',
            )
        ),
        (
            pytest.param(
                '300500',
                {
                    'payment_methods': [
                        {
                            'type': 'card',
                            'name': 'VISA',
                            'short_title': '** visa 4242',
                            'id': 'card-x8e000cd57550021906e9ee43',
                            'bin': '424242',
                            'currency': 'RUB',
                            'system': 'VISA',
                            'number': '424242****4242',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'service_token': 'testtoken',
                        },
                        {
                            'type': 'card',
                            'name': 'MasterCard',
                            'short_title': '** visa 4444',
                            'id': 'card-x8e000cd57550021906e9ee44',
                            'bin': '555555',
                            'currency': 'RUB',
                            'system': 'MasterCard',
                            'number': '555555****4444',
                            'availability': {
                                'available': False,
                                'disabled_reason': 'Мок оплат',
                            },
                            'service_token': 'testtoken2',
                        },
                        {
                            'type': 'applepay',
                            'name': 'applepay',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'merchant_id_list': [
                                'merchant.ru.yandex.ytaxi.trust',
                                'merchant.ru.yandex.mobile.development',
                                'merchant.ru.yandex.taxi.develop',
                            ],
                            'service_token': 'tokenapple',
                        },
                        {
                            'type': 'googlepay',
                            'name': 'googlepay',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'merchant_id': 'merchant.ru.yandex.ytaxi.trust',
                            'service_token': 'google',
                        },
                        {
                            'type': 'sbp',
                            'name': 'sbp',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                        },
                        {
                            'type': 'corp',
                            'name': 'Кабинет для QA Еды',
                            'id': 'corp:7c3a629872d944d8b7fad154aff37b14:RUB',
                            'currency': 'RUB',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'description': '',
                        },
                        {
                            'type': 'personal_wallet',
                            'name': 'Плюс',
                            'id': 'w/031bb88c-2e53-5f95-a2f6-82b6886c61f2',
                            'availability': {
                                'available': False,
                                'disabled_reason': 'Мок оплат',
                            },
                            'description': '1154',
                            'currency_rules': {
                                'code': 'RUB',
                                'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
                                'text': 'руб.',
                                'sign': '₽',
                            },
                        },
                    ],
                    'last_used_payment_method': {
                        'type': 'card',
                        'id': 'card-x8e000cd57550021906e9ee43',
                    },
                    'region_id': 51,
                },
                id='uid not in DB',
            )
        ),
    ],
)
async def test_lpm(
        taxi_eats_testing_simplifier_responser_web,
        uid,
        expected_response_json,
):
    response = await taxi_eats_testing_simplifier_responser_web.post(
        path='/v1/payment-methods/availability',
        headers={'X-Remote-IP': '127.0.0.1', 'X-Yandex-UID': uid},
        json={
            'sender_point': [37.62, 55.75],
            'destination_point': [37.62, 55.75],
            'region_id': 51,
            'order_info': {
                'currency': 'RUB',
                'item_sets': [{'items_type': 'food', 'amount': '111.00'}],
            },
            'place_info': {'accepts_cash': True},
        },
    )
    assert response.status == 200, await response.json()
    assert await response.json() == expected_response_json


async def test_lpm_bad_request(taxi_eats_testing_simplifier_responser_web):
    response = await taxi_eats_testing_simplifier_responser_web.post(
        path='/v1/payment-methods/availability',
        headers={'X-Remote-IP': '127.0.0.1', 'X-Yandex-UID': '1'},
        json={
            'sender_point': [37.62, 55.75],
            'destination_point': [37.62, 55.75],
            'region_id': 51,
            'place_info': {'accepts_cash': True},
        },
    )
    assert response.status == 400, await response.json()
