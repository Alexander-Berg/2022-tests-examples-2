import pytest


@pytest.mark.pgsql(
    'eats_corp_orders', files=['pg_eats_corp_orders.sql', 'orders.sql'],
)
@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        (
            {'order_id': 'order_1'},
            200,
            {
                'order_id': 'order_1',
                'amount': '100',
                'payment_status': 'completed',
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
                'payment_methods': [
                    {
                        'type': 'corp',
                        'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
                        'amount': '100',
                    },
                ],
                'place_info': {
                    'place_id': '146',
                    'overspending_enabled': True,
                },
                'items': [
                    {
                        'price': '100.0',
                        'quantity': '1.0',
                        'tin': '',
                        'title': 'Мороженое',
                        'vat': 'nds_0',
                    },
                ],
                'originator': 'terminal',
            },
        ),
        (
            {'order_id': 'order_2'},
            200,
            {
                'order_id': 'order_2',
                'amount': '100',
                'payment_status': 'completed',
                'created_at': '2022-02-02T00:00:00+03:00',
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
                'payment_methods': [
                    {
                        'type': 'corp',
                        'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
                        'amount': '1',
                    },
                    {
                        'type': 'card',
                        'id': 'card-xad5238801592dea1e69f1488',
                        'amount': '99',
                    },
                ],
                'place_info': {
                    'place_id': '146',
                    'overspending_enabled': True,
                },
                'items': [
                    {
                        'price': '100.0',
                        'quantity': '1.0',
                        'tin': '',
                        'title': 'Мороженое',
                        'vat': 'nds_0',
                    },
                ],
                'originator': 'terminal',
            },
        ),
        (
            {'order_id': 'order_3'},
            200,
            {
                'order_id': 'order_3',
                'amount': '100',
                'payment_status': 'completed',
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
                'payment_methods': [
                    {
                        'amount': '100',
                        'id': 'card-xad5238801592dea1e69f1488',
                        'type': 'card',
                    },
                ],
                'place_info': {
                    'place_id': '146',
                    'overspending_enabled': True,
                },
                'items': [
                    {
                        'price': '100.0',
                        'quantity': '1.0',
                        'tin': '',
                        'title': 'Мороженое',
                        'vat': 'nds_0',
                    },
                ],
                'originator': 'terminal',
            },
        ),
        ({'order_id': 'not fount'}, 404, {}),
    ],
)
async def test_admin_order_get(
        taxi_eats_corp_orders_web,
        mock_eats_eaters,
        params,
        expected_status,
        expected_json,
):
    @mock_eats_eaters('/v1/eaters/find-by-id')
    async def _mock_find_eater_by_ids(request):
        id_ = request.json['id']
        return {
            'eater': {
                'created_at': '2022-02-01T00:00:00+03:00',
                'id': f'{id_}',
                'updated_at': '2022-02-01T00:00:00+03:00',
                'uuid': f'uuid_{id_}',
                'personal_phone_id': f'personal_phone_{id_}',
                'personal_email_id': f'personal_email_{id_}',
            },
        }

    response = await taxi_eats_corp_orders_web.get(
        '/v1/admin/order', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
