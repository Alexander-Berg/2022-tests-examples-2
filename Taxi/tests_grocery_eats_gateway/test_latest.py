import pytest


from tests_grocery_eats_gateway import headers


ORDER_ID = 'order_id'
SHORT_ORDER_ID = 'short_order_id'
ORDER_ADDRESS = 'some street, 10'
NOW = '2021-01-01T21:03:00+00:00'


GROCERY_ORDER_WITH_ITEM = {
    'order_id': ORDER_ID,
    'short_order_id': SHORT_ORDER_ID,
    'yandex_uid': 'yandex_uid',
    'created_at': '2020-12-31T21:00:00.778583+00:00',
    'status': 'closed',
    'closed_at': '2020-12-31T22:00:00.778583+00:00',
    'calculation': {
        'items': [
            {'name': 'kakao', 'cost': '200.00', 'product_id': 'product_1'},
        ],
        'final_cost': '123',
        'discount': '0',
        'refund': '0',
        'currency_code': 'RUB',
    },
    'contact': {},
    'legal_entities': [],
    'destinations': [{'point': [0, 0], 'short_text': ORDER_ADDRESS}],
    'receipts': [{'title': 'receipt_title', 'receipt_url': 'receipt_url'}],
    'depot_id': '70134',
}


@pytest.mark.now(NOW)
async def test_latest_basic(
        taxi_grocery_eats_gateway,
        grocery_order_log,
        overlord_catalog,
        mockserver,
        load_json,
):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_grocery_order_log(request):
        return {'orders': load_json('grocery_order_log.json')}

    response = await taxi_grocery_eats_gateway.post(
        '/grocery-eats-gateway/v1/latest',
        json={'order_count': 3, 'day_count': 1},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status == 200, response
    assert mock_grocery_order_log.times_called == 1
    assert len(response.json()) == 2
    assert response.json() == load_json('expected_test_basic_response.json')
