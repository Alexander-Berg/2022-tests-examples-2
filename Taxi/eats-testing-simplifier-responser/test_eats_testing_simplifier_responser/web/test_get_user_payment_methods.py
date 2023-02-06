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
# pylint: disable=import-only-modules
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
    'passport_uid, result,status_code',
    [
        pytest.param(
            1,
            {
                'mock_usage': True,
                'payment_methods': [
                    {'enable': True, 'id': 'VISA'},
                    {'enable': False, 'id': 'MASTERCARD'},
                    {'enable': True, 'id': 'googlepay'},
                ],
                'uid': '1',
            },
            200,
            id='get more than one payment methods',
        ),
        pytest.param(
            2,
            {
                'mock_usage': True,
                'payment_methods': [{'enable': True, 'id': 'corp'}],
                'uid': '2',
            },
            200,
            id='get one payment methods',
        ),
        pytest.param(
            3,
            {
                'mock_usage': True,
                'payment_methods': [{'enable': True, 'id': 'corp'}],
                'uid': '2',
            },
            200,
            id='No record in DB',
            marks=pytest.mark.skip,
        ),
        pytest.param(
            4,
            {
                'mock_usage': False,
                'payment_methods': [
                    {'id': 'card-x8e000cd57550021906e9ee43', 'enable': True},
                    {'id': 'card-x8e000cd57550021906e9ee44', 'enable': False},
                    {'id': 'applepay', 'enable': True},
                    {'id': 'googlepay', 'enable': True},
                    {'id': 'sbp', 'enable': True},
                    {
                        'id': 'corp:7c3a629872d944d8b7fad154aff37b14:RUB',
                        'enable': True,
                    },
                    {
                        'id': 'w/031bb88c-2e53-5f95-a2f6-82b6886c61f2',
                        'enable': False,
                    },
                ],
                'uid': '4',
            },
            200,
            id='No record in DB',
        ),
    ],
)
async def test_get_payment_methods(
        taxi_eats_testing_simplifier_responser_web,
        passport_uid,
        result,
        status_code,
):
    response = await taxi_eats_testing_simplifier_responser_web.get(
        path='/users/payments-methods', params={'passport_uid': passport_uid},
    )
    assert response.status == status_code, response.text
    assert await response.json() == result


async def test_post_payment_methods(
        taxi_eats_testing_simplifier_responser_web,
):
    response1 = await taxi_eats_testing_simplifier_responser_web.get(
        path='/users/payments-methods', params={'passport_uid': 1},
    )

    response = await taxi_eats_testing_simplifier_responser_web.post(
        path='/users/payments-methods',
        json={
            'uid': '1',
            'mock_usage': True,
            'payment_methods': [{'id': 'VISA1', 'enable': False}],
        },
    )
    assert response.status == 200, 'Response code should be 200'

    response2 = await taxi_eats_testing_simplifier_responser_web.get(
        path='/users/payments-methods', params={'passport_uid': 1},
    )

    assert await response.json() == {}
    assert await response1.json() != await response2.json()
