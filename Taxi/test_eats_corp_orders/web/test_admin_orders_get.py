import pytest

EATERS = [
    {
        'created_at': '2022-02-01T00:00:00+03:00',
        'id': '1',
        'updated_at': '2022-02-01T00:00:00+03:00',
        'uuid': 'uuid_1',
        'personal_phone_id': 'personal_phone_1',
        'personal_email_id': f'personal_email_1',
    },
    {
        'created_at': '2022-02-02T00:00:00+03:00',
        'id': '2',
        'updated_at': '2022-02-02T00:00:00+03:00',
        'uuid': 'uuid_2',
    },
]


@pytest.mark.pgsql(
    'eats_corp_orders', files=['pg_eats_corp_orders.sql', 'orders.sql'],
)
@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        (
            {'limit': 1},
            200,
            {
                'orders': [
                    {
                        'order_id': 'order_6',
                        'amount': '100',
                        'payment_status': 'completed',
                        'payment_methods': [],
                        'created_at': '2022-02-06T00:00:00+03:00',
                        'code_type': 'qr',
                        'user_info': {'user_id': '2'},
                        'place_info': {'place_id': '146'},
                        'items': [],
                        'originator': 'terminal',
                    },
                ],
                'has_more': True,
            },
        ),
        (
            {
                'datetime_from': '2022-02-03 00:00:00+03:00',
                'datetime_to': '2022-02-04 00:00:00+03:00',
            },
            200,
            {
                'orders': [
                    {
                        'order_id': 'order_4',
                        'amount': '100',
                        'payment_status': 'completed',
                        'payment_methods': [],
                        'created_at': '2022-02-04T00:00:00+03:00',
                        'code_type': 'qr',
                        'user_info': {'user_id': '2'},
                        'place_info': {'place_id': '146'},
                        'items': [],
                        'originator': 'terminal',
                    },
                    {
                        'order_id': 'order_3',
                        'amount': '100',
                        'payment_status': 'completed',
                        'payment_methods': [
                            {
                                'amount': '100',
                                'id': (
                                    'corp:916880dd88914f3b836e1a289484c834:RUB'
                                ),
                                'type': 'corp',
                            },
                        ],
                        'created_at': '2022-02-03T00:00:00+03:00',
                        'code_type': 'qr',
                        'user_info': {
                            'balance_full': '1000',
                            'balance_left': '500',
                            'limit_type': 'day',
                            'organization': 'Yandex Badge',
                            'user_id': '1',
                            'email_id': 'personal_email_1',
                            'phone_id': 'personal_phone_1',
                            'overspending_enabled': True,
                        },
                        'place_info': {
                            'place_id': '146',
                            'overspending_enabled': True,
                        },
                        'items': [],
                        'originator': 'terminal',
                    },
                ],
                'has_more': False,
            },
        ),
        (
            {'order_ids': 'order_1,order_5'},
            200,
            {
                'orders': [
                    {
                        'order_id': 'order_5',
                        'amount': '100',
                        'payment_status': 'completed',
                        'payment_methods': [
                            {
                                'amount': '100',
                                'id': (
                                    'corp:916880dd88914f3b836e1a289484c834:RUB'
                                ),
                                'type': 'corp',
                            },
                        ],
                        'created_at': '2022-02-05T00:00:00+03:00',
                        'code_type': 'qr',
                        'user_info': {
                            'balance_full': '1000',
                            'balance_left': '500',
                            'limit_type': 'day',
                            'organization': 'Yandex Badge',
                            'user_id': '1',
                            'email_id': 'personal_email_1',
                            'phone_id': 'personal_phone_1',
                            'overspending_enabled': True,
                        },
                        'place_info': {
                            'place_id': '146',
                            'overspending_enabled': True,
                        },
                        'items': [],
                        'originator': 'terminal',
                    },
                    {
                        'order_id': 'order_1',
                        'amount': '100',
                        'payment_status': 'completed',
                        'payment_methods': [
                            {
                                'amount': '100',
                                'id': (
                                    'corp:916880dd88914f3b836e1a289484c834:RUB'
                                ),
                                'type': 'corp',
                            },
                        ],
                        'created_at': '2022-02-01T00:00:00+03:00',
                        'code_type': 'qr',
                        'user_info': {
                            'balance_full': '1000',
                            'balance_left': '500',
                            'limit_type': 'day',
                            'organization': 'Yandex Badge',
                            'user_id': '1',
                            'email_id': 'personal_email_1',
                            'phone_id': 'personal_phone_1',
                            'overspending_enabled': True,
                        },
                        'place_info': {
                            'place_id': '146',
                            'overspending_enabled': True,
                        },
                        'items': [],
                        'originator': 'terminal',
                    },
                ],
                'has_more': False,
            },
        ),
        (
            {
                'datetime_from': '2022-02-02 00:00:00+03:00',
                'datetime_to': '2022-02-04 00:00:00+03:00',
                'phone_ids': 'personal_phone_1',
            },
            200,
            {
                'orders': [
                    {
                        'order_id': 'order_3',
                        'amount': '100',
                        'payment_status': 'completed',
                        'payment_methods': [
                            {
                                'amount': '100',
                                'id': (
                                    'corp:916880dd88914f3b836e1a289484c834:RUB'
                                ),
                                'type': 'corp',
                            },
                        ],
                        'created_at': '2022-02-03T00:00:00+03:00',
                        'code_type': 'qr',
                        'user_info': {
                            'balance_full': '1000',
                            'balance_left': '500',
                            'limit_type': 'day',
                            'organization': 'Yandex Badge',
                            'user_id': '1',
                            'email_id': 'personal_email_1',
                            'phone_id': 'personal_phone_1',
                            'overspending_enabled': True,
                        },
                        'place_info': {
                            'place_id': '146',
                            'overspending_enabled': True,
                        },
                        'items': [],
                        'originator': 'terminal',
                    },
                ],
                'has_more': False,
            },
        ),
    ],
)
async def test_admin_orders_get(
        taxi_eats_corp_orders_web,
        mock_eats_eaters,
        params,
        expected_status,
        expected_json,
):
    @mock_eats_eaters('/v1/eaters/find-by-personal-phone-id')
    async def _mock_find_eater_by_phone_id(request):
        personal_phone_id = request.json['personal_phone_id']
        return {
            'eaters': [
                eater
                for eater in EATERS
                if eater.get('personal_phone_id') == personal_phone_id
            ],
            'pagination': {'limit': 10, 'has_more': False},
        }

    @mock_eats_eaters('/v1/eaters/find-by-ids')
    async def _mock_find_eater_by_ids(request):
        return {
            'eaters': [
                eater for eater in EATERS if eater['id'] in request.json['ids']
            ],
            'pagination': {'limit': 10, 'has_more': False},
        }

    response = await taxi_eats_corp_orders_web.get(
        '/v1/admin/orders', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
