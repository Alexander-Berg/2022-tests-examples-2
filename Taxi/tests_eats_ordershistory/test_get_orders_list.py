import pytest

CONFIG_REASONS = {
    'reasons': {'reason1': 'full_reason_1', 'reason2': 'full_reason_2'},
}


def make_order_response(
        order_id,
        place_id,
        status,
        created_at,
        feedback=None,
        cart=None,
        delivery_address=None,
        cancel_reason=None,
        flow_type=None,
):
    order = {
        'order_id': ('order-id-' + order_id),
        'source': 'eda',
        'place_id': place_id,
        'status': status,
        'delivery_location': {'lat': 1.0, 'lon': 1.0},
        'total_amount': '123.45',
        'is_asap': True,
        'created_at': created_at,
    }
    if feedback is not None:
        order['feedback'] = feedback
    if cart is not None:
        order['cart'] = cart
    if delivery_address is not None:
        order['delivery_address'] = delivery_address
    if cancel_reason is not None:
        order['cancel_reason'] = cancel_reason
    if flow_type is not None:
        order['flow_type'] = flow_type
    return order


def make_cart(name, place_menu_item_id, quantity, origin_id, catalog_type):
    return {
        'name': name,
        'place_menu_item_id': place_menu_item_id,
        'quantity': quantity,
        'origin_id': origin_id,
        'catalog_type': catalog_type,
        'product_id': origin_id,
    }


@pytest.mark.parametrize(
    ' etalon_request, etalon_response, status',
    [
        pytest.param(
            {'filters': {}},
            {'orders': []},
            200,
            id='empty db',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_no_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {'filters': {}, 'projection': ['feedback']},
            {
                'orders': [
                    make_order_response(
                        '1', 123, 'delivered', '2021-07-20T12:01:00+00:00', {},
                    ),
                ],
            },
            200,
            id='one order',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_one_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {'filters': {}, 'projection': ['cart', 'cancel_reason']},
            {
                'orders': [
                    make_order_response(
                        '2',
                        456,
                        'cancelled',
                        '2021-07-25T12:01:00+00:00',
                        None,
                        [
                            make_cart('eda-item', 1, 1, '1', 'core_catalog'),
                            make_cart('eda-item', 2, 1, '2', 'core_catalog'),
                            make_cart('eda-item', 3, 1, '3', 'core_catalog'),
                        ],
                    ),
                    make_order_response(
                        '1',
                        123,
                        'delivered',
                        '2021-07-20T12:01:00+00:00',
                        None,
                        [
                            make_cart('eda-item', 1, 1, '1', 'core_catalog'),
                            make_cart('eda-item', 2, 1, '2', 'core_catalog'),
                            make_cart('eda-item', 3, 1, '3', 'core_catalog'),
                        ],
                    ),
                ],
            },
            200,
            id='two order',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_two_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {'filters': {}, 'projection': ['cart', 'cancel_reason']},
            {
                'orders': [
                    make_order_response(
                        '2',
                        456,
                        'cancelled',
                        '2021-07-25T12:01:00+00:00',
                        None,
                        [
                            make_cart('eda-item', 1, 1, '1', 'core_catalog'),
                            make_cart('eda-item', 2, 1, '2', 'core_catalog'),
                            make_cart('eda-item', 3, 1, '3', 'core_catalog'),
                        ],
                        cancel_reason='full_reason_1',
                    ),
                    make_order_response(
                        '1',
                        123,
                        'delivered',
                        '2021-07-20T12:01:00+00:00',
                        None,
                        [
                            make_cart('eda-item', 1, 1, '1', 'core_catalog'),
                            make_cart('eda-item', 2, 1, '2', 'core_catalog'),
                            make_cart('eda-item', 3, 1, '3', 'core_catalog'),
                        ],
                    ),
                ],
            },
            200,
            id='two order with config',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_two_order.sql'],
                ),
                pytest.mark.config(
                    EATS_ORDERSHISTORY_CANCEL_REASONS=CONFIG_REASONS,
                ),
            ),
        ),
        pytest.param(
            {
                'filters': {'order_ids': ['order-id-2']},
                'projection': ['feedback', 'cart', 'delivery_address'],
            },
            {
                'orders': [
                    make_order_response(
                        '2',
                        456,
                        'cancelled',
                        '2021-07-25T12:01:00+00:00',
                        {},
                        [
                            make_cart('eda-item', 1, 1, '1', 'core_catalog'),
                            make_cart('eda-item', 2, 1, '2', 'core_catalog'),
                            make_cart('eda-item', 3, 1, '3', 'core_catalog'),
                        ],
                        {
                            'comment': 'comment2',
                            'floor': '4',
                            'full_address': 'address2',
                            'office': '13',
                        },
                    ),
                ],
            },
            200,
            id='four order, one result, one order_id',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_four_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {'filters': {'place_ids': [123]}, 'projection': []},
            {
                'orders': [
                    make_order_response(
                        '3', 123, 'delivered', '2021-07-29T12:01:00+00:00',
                    ),
                    make_order_response(
                        '1', 123, 'delivered', '2021-07-20T12:01:00+00:00',
                    ),
                ],
            },
            200,
            id='four order, two result, one place_id',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_four_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {'filters': {'statuses': ['delivered']}},
            {
                'orders': [
                    make_order_response(
                        '1', 123, 'delivered', '2021-07-20T12:01:00+00:00',
                    ),
                ],
            },
            200,
            id='two order, one result, status',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_two_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {'filters': {'place_ids': [456], 'statuses': ['delivered']}},
            {
                'orders': [
                    make_order_response(
                        '4', 456, 'delivered', '2021-07-29T12:01:00+00:00',
                    ),
                ],
            },
            200,
            id='four order, one result, place_id+status',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_four_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'filters': {
                    'period': {
                        'from': '2021-07-21T12:01:00Z',
                        'to': '2021-07-28T12:01:00Z',
                    },
                },
            },
            {
                'orders': [
                    make_order_response(
                        '2', 456, 'cancelled', '2021-07-25T12:01:00+00:00',
                    ),
                ],
            },
            200,
            id='two order, one result, date filter',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_two_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'filters': {
                    'place_ids': [123],
                    'period': {
                        'from': '2021-07-19T12:01:00Z',
                        'to': '2021-07-28T12:01:00Z',
                    },
                },
            },
            {
                'orders': [
                    make_order_response(
                        '1', 123, 'delivered', '2021-07-20T12:01:00+00:00',
                    ),
                ],
            },
            200,
            id='two order, one result, date filter + place_id',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_two_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'filters': {
                    'pagination': {
                        'limit': 1,
                        'cursor': (
                            '{"order_id": "order-id-3", '
                            '"created_at": "2021-07-26T12:01:00+00:00"}'
                        ),
                    },
                },
            },
            {
                'orders': [
                    make_order_response(
                        '2', 456, 'cancelled', '2021-07-25T12:01:00+00:00',
                    ),
                ],
            },
            200,
            id='four order, one result, pagination',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_four_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'filters': {
                    'statuses': ['delivered'],
                    'pagination': {
                        'limit': 1,
                        'cursor': (
                            '{"order_id": "order-id-3", '
                            '"created_at": "2021-07-26T12:01:00+00:00"}'
                        ),
                    },
                },
            },
            {
                'orders': [
                    make_order_response(
                        '1', 123, 'delivered', '2021-07-20T12:01:00+00:00',
                    ),
                ],
            },
            200,
            id='four order, one result, pagination + status',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_four_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {'filters': {'pagination': {'limit': 1, 'cursor': '{}'}}},
            {
                'orders': [
                    make_order_response(
                        '4', 456, 'delivered', '2021-07-29T12:01:00+00:00',
                    ),
                ],
            },
            200,
            id='four order, one result, empty cursor',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_four_order.sql'],
                ),
            ),
        ),
        pytest.param(
            {
                'filters': {'flow_types': ['native']},
                'projection': ['feedback'],
            },
            {
                'orders': [
                    make_order_response(
                        '1',
                        123,
                        'delivered',
                        '2021-07-20T12:01:00+00:00',
                        {},
                        flow_type='native',
                    ),
                ],
            },
            200,
            id='one order with flow_type',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_one_order_with_flow.sql'],
                ),
            ),
        ),
        pytest.param(
            {'filters': {'eater_ids': [1, 2, 3]}},
            {
                'orders': [
                    make_order_response(
                        '3', 123, 'delivered', '2021-07-29T12:01:00+00:00',
                    ),
                    make_order_response(
                        '2', 456, 'cancelled', '2021-07-25T12:01:00+00:00',
                    ),
                    make_order_response(
                        '1', 123, 'delivered', '2021-07-20T12:01:00+00:00',
                    ),
                ],
            },
            200,
            id='3 orders with eater_ids',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=['pg_eats_ordershistory_with_eater_ids.sql'],
                ),
            ),
        ),
    ],
)
async def test_get_orders_list(
        taxi_eats_ordershistory, etalon_request, etalon_response, status,
):
    response = await taxi_eats_ordershistory.post(
        '/internal/v1/get-orders/list', json=etalon_request,
    )
    assert response.status_code == status
    if status == 200:
        json = response.json()
        assert json == etalon_response
