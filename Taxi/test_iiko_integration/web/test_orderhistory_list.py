import pytest

from test_iiko_integration import stubs


URL = '/iiko-integration/v1/orderhistory/list'

ORDERS = {
    'held_and_confirmed': {
        'data': {
            'order_id': 'held_2',
            'created_at': '2020-06-06T12:05:00+03:00',
            'title': 'Ресторан 01',
            'status': 'paid',
            'payment': {
                'final_cost': '100,00 $SIGN$$CURRENCY$',
                'cashback': '1',
                'currency_code': 'RUB',
            },
        },
        'service': 'qr_pay',
    },
    'clearing': {
        'data': {
            'order_id': 'clearing',
            'created_at': '2020-06-04T12:05:00+03:00',
            'title': 'Ресторан 01',
            'status': 'paid',
            'payment': {
                'final_cost': '300,00 $SIGN$$CURRENCY$',
                'cashback': '18',
                'currency_code': 'RUB',
            },
        },
        'service': 'qr_pay',
    },
    'cleared1': {
        'data': {
            'order_id': 'cleared1',
            'created_at': '2020-06-03T12:05:00+03:00',
            'title': 'Ресторан 01',
            'status': 'paid',
            'payment': {
                'final_cost': '400,00 $SIGN$$CURRENCY$',
                'cashback': '36',
                'currency_code': 'RUB',
            },
        },
        'service': 'qr_pay',
    },
    'cleared2': {
        'data': {
            'order_id': 'cleared2',
            'created_at': '2020-06-03T12:05:00+03:00',
            'title': 'Ресторан 01',
            'status': 'paid',
            'payment': {
                'final_cost': '500,00 $SIGN$$CURRENCY$',
                'cashback': '55',
                'currency_code': 'RUB',
            },
        },
        'service': 'qr_pay',
    },
    'cleared3': {
        'data': {
            'order_id': 'cleared3',
            'created_at': '2020-06-01T12:05:00+03:00',
            'title': 'Ресторан 01',
            'status': 'paid',
            'payment': {
                'final_cost': '200,00 $SIGN$$CURRENCY$',
                'currency_code': 'RUB',
            },
        },
        'service': 'qr_pay',
    },
}


@pytest.mark.config(
    **stubs.RESTAURANT_INFO_CONFIGS,
    CURRENCY_FORMATTING_RULES=stubs.CURRENCY_FORMATTING_RULES,
)
@pytest.mark.translations(**stubs.ORDERHISTORY_TRANSLATIONS)
@pytest.mark.parametrize(
    (
        'yandex_uids',
        'older_than',
        'expected_status',
        'expected_orders',
        'include_service_metadata',
    ),
    (
        pytest.param(
            ['user1', 'user1_bound1', 'user1_bound2'],
            None,
            200,
            [
                ORDERS['held_and_confirmed'],
                ORDERS['clearing'],
                ORDERS['cleared1'],
            ],
            True,
            id='normal work',
        ),
        pytest.param(
            ['user1', 'user1_bound1', 'user1_bound2'],
            {'order_id': 'cleared1', 'created_at': 1591164300},
            200,
            [ORDERS['cleared2'], ORDERS['cleared3']],
            True,
            id='normal work with older_than',
        ),
        pytest.param(
            ['user1', 'user1_bound1', 'user1_bound2'],
            {'order_id': 'cleared3', 'created_at': 1590991500},
            200,
            [],
            False,
            id='normal work without metadata',
        ),
        pytest.param(
            ['user3'],
            None,
            200,
            [],
            True,
            id='normal work for user without orders',
        ),
        pytest.param(
            ['user4'],
            None,
            200,
            [],
            False,
            id='can not load order, no translations',
        ),
        pytest.param(
            ['user3'],
            {'order_id': 'wrong_order', 'created_at': 1599991500},
            404,
            [],
            True,
            id='Order not found for user_id',
        ),
    ),
)
async def test(
        web_app_client,
        yandex_uids,
        older_than,
        expected_status,
        expected_orders,
        include_service_metadata,
):
    request_body = {'range': {'results_count': 3}}
    if include_service_metadata:
        request_body['include_service_metadata'] = include_service_metadata
    if older_than:
        request_body['range']['older_than'] = older_than
    bound_uids = ','.join(yandex_uids[1::]) if len(yandex_uids) > 1 else ''
    headers = {
        'X-Yandex-UID': yandex_uids[0],
        'X-YaTaxi-Bound-Uids': bound_uids,
        'X-Request-Language': 'ru',
    }
    response = await web_app_client.post(
        URL, json=request_body, headers=headers,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    content = await response.json()

    assert content['orders'] == expected_orders
    # not send metadata if user has not orders or older_than is in request
    if include_service_metadata and expected_orders and not older_than:
        last_order_id = 'held_1'
        assert content['service_metadata'] == {
            'service': 'qr_pay',
            'name': 'QR оплата',
            'last_order_id': last_order_id,
        }
    else:
        assert not content.get('service_metadata')
