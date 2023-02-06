import pytest

PAYMENT_METHODS = [
    {
        'availability': {'available': True, 'disabled_reason': ''},
        'balance_full': '1000',
        'balance_left': '500',
        'balance_period': 'day',
        'currency': 'RUB',
        'currency_sign': '₽',
        'description': 'Осталось 500 из 1000 ₽',
        'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
        'name': 'corp-test',
        'type': 'corp',
    },
    {
        'availability': {'available': True, 'disabled_reason': ''},
        'currency': 'RUB',
        'currency_sign': '₽',
        'description': '',
        'id': 'badge:yandex_badge:RUB',
        'name': 'Yandex Badge',
        'type': 'corp',
    },
]


@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        (
            {'location': [37.1, 59.2]},
            200,
            {'payment_methods': PAYMENT_METHODS},
        ),
        ({}, 200, {'payment_methods': PAYMENT_METHODS}),
    ],
)
async def test_get_corp_payment_methods(
        taxi_eats_corp_orders_web,
        mock_eats_taxi_corp_integration,
        mock_payment_methods,
        mock_corp_users,
        eats_user,
        yandex_uid,
        user_agent,
        params,
        expected_status,
        expected_json,
):
    @mock_eats_taxi_corp_integration('/v1/payment-methods/eats')
    async def _payment_methods_eats(request):
        return {
            'payment_methods': [
                {
                    'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
                    'type': 'corp',
                    'name': 'corp-test',
                    'currency': 'RUB',
                    'availability': {'available': True, 'disabled_reason': ''},
                    'description': 'Осталось 500 из 1000 ₽',
                    'client_id': 'beed2277ae71428db1029c07394e542c',
                    'user_id': '916880dd88914f3b836e1a289484c834',
                    'balance_left': '500',
                },
            ],
        }

    @mock_payment_methods('/v1/superapp-available-payment-types')
    async def _available_payment_types(request):
        return {'payment_types': ['card', 'corp', 'badge'], 'merchant_ids': []}

    @mock_corp_users('/v1/users-limits/eats/fetch')
    async def _users_limits(request):
        return {
            'users': [
                {
                    'id': '916880dd88914f3b836e1a289484c834',
                    'client_id': 'beed2277ae71428db1029c07394e542c',
                    'client_name': 'corp-test',
                    'limits': [
                        {
                            'limit_id': 'limit_id',
                            'limits': {
                                'orders_cost': {
                                    'currency': 'RUB',
                                    'currency_sign': '₽',
                                    'balance': '500',
                                    'value': '1000',
                                    'period': 'day',
                                },
                            },
                        },
                    ],
                },
            ],
        }

    response = await taxi_eats_corp_orders_web.post(
        '/v1/payment-method/get-corp',
        headers={
            'X-Eats-User': eats_user,
            'X-Yandex-UID': yandex_uid,
            'X-Remote-IP': '',
            'User-Agent': user_agent,
        },
        json=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
