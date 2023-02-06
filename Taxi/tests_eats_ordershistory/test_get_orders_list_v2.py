import pytest

CONFIG_REASONS = {
    'reasons': {'reason1': 'full_reason_1', 'reason2': 'full_reason_2'},
}

ORDER_WITH_SHIPPING_TYPE_DATA = (
    'pg_eats_ordershistory_one_order_with_shipping_type.sql'
)


def make_order_response(
        order_id,
        place_id,
        status,
        created_at,
        feedback=None,
        cart=None,
        delivery_address=None,
        cancel_reason=None,
        shipping_type=None,
        cancelled_at=None,
        ready_to_delivery_at=None,
        taken_at=None,
):
    order = {
        'order_id': ('order-id-' + order_id),
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
    if shipping_type is not None:
        order['shipping_type'] = shipping_type
    if cancelled_at is not None:
        order['cancelled_at'] = cancelled_at
    if ready_to_delivery_at is not None:
        order['ready_to_delivery_at'] = ready_to_delivery_at
    if taken_at is not None:
        order['taken_at'] = taken_at
    return order


def make_cart(
        name,
        quantity,
        origin_id,
        catalog_type,
        original_quantity=None,
        measure_unit=None,
        parent_origin_id=None,
        cost_for_customer=None,
        refunded_amount=None,
        standalone_parent_origin_id=None,
        weight=None,
        original_weight=None,
):
    cart = {
        'name': name,
        'quantity': quantity,
        'origin_id': origin_id,
        'catalog_type': catalog_type,
    }

    if original_quantity is not None:
        cart['original_quantity'] = original_quantity
    if measure_unit is not None:
        cart['measure_unit'] = measure_unit
    if parent_origin_id is not None:
        cart['parent_origin_id'] = parent_origin_id
    if cost_for_customer is not None:
        cart['cost_for_customer'] = cost_for_customer
    if refunded_amount is not None:
        cart['refunded_amount'] = refunded_amount
    if standalone_parent_origin_id is not None:
        cart['standalone_parent_origin_id'] = standalone_parent_origin_id
    if weight is not None:
        cart['weight'] = weight
    if original_weight is not None:
        cart['original_weight'] = original_weight

    return cart


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
                        '1', 123, 'finished', '2021-07-20T12:01:00+00:00', {},
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
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='1',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='2',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='3',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='-1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                        ],
                        cancelled_at='2021-07-25T13:01:00+00:00',
                    ),
                    make_order_response(
                        '1',
                        123,
                        'finished',
                        '2021-07-20T12:01:00+00:00',
                        None,
                        [
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='1',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='2',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='3',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
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
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='1',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='2',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='3',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='-1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                        ],
                        cancel_reason='full_reason_1',
                        cancelled_at='2021-07-25T13:01:00+00:00',
                    ),
                    make_order_response(
                        '1',
                        123,
                        'finished',
                        '2021-07-20T12:01:00+00:00',
                        None,
                        [
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='1',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='2',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='3',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                                weight=1.00,
                                original_weight=0.5,
                            ),
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
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='1',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='2',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                            ),
                            make_cart(
                                name='eda-item',
                                quantity=1,
                                origin_id='3',
                                catalog_type='core_catalog',
                                original_quantity=2,
                                measure_unit='count',
                                parent_origin_id=None,
                                cost_for_customer='1',
                                refunded_amount='1',
                                standalone_parent_origin_id=None,
                            ),
                        ],
                        {
                            'comment': 'comment2',
                            'floor': '4',
                            'full_address': 'address2',
                            'office': '13',
                        },
                        cancelled_at='2021-07-25T13:01:00+00:00',
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
                        '3', 123, 'finished', '2021-07-29T12:01:00+00:00',
                    ),
                    make_order_response(
                        '1', 123, 'finished', '2021-07-20T12:01:00+00:00',
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
            {'filters': {'statuses': ['finished']}},
            {
                'orders': [
                    make_order_response(
                        '1', 123, 'finished', '2021-07-20T12:01:00+00:00',
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
            {'filters': {'place_ids': [456], 'statuses': ['created']}},
            {
                'orders': [
                    make_order_response(
                        '4', 456, 'created', '2021-07-29T12:01:00+00:00',
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
                        '2',
                        456,
                        'cancelled',
                        '2021-07-25T12:01:00+00:00',
                        cancelled_at='2021-07-25T13:01:00+00:00',
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
                        '1', 123, 'finished', '2021-07-20T12:01:00+00:00',
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
                        '2',
                        456,
                        'cancelled',
                        '2021-07-25T12:01:00+00:00',
                        cancelled_at='2021-07-25T13:01:00+00:00',
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
                    'statuses': ['finished'],
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
                        '1', 123, 'finished', '2021-07-20T12:01:00+00:00',
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
                        '4', 456, 'created', '2021-07-29T12:01:00+00:00',
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
                'filters': {'shipping_types': ['delivery']},
                'projection': ['feedback'],
            },
            {
                'orders': [
                    make_order_response(
                        '1',
                        123,
                        'finished',
                        '2021-07-20T12:01:00+00:00',
                        {},
                        shipping_type='delivery',
                    ),
                ],
            },
            200,
            id='one order with shipping_type',
            marks=(
                pytest.mark.pgsql(
                    'eats_ordershistory',
                    files=[ORDER_WITH_SHIPPING_TYPE_DATA],
                ),
            ),
        ),
        pytest.param(
            {'filters': {'eater_ids': [1, 2, 3]}},
            {
                'orders': [
                    make_order_response(
                        '3', 123, 'finished', '2021-07-29T12:01:00+00:00',
                    ),
                    make_order_response(
                        '2', 456, 'cancelled', '2021-07-25T12:01:00+00:00',
                    ),
                    make_order_response(
                        '1', 123, 'finished', '2021-07-20T12:01:00+00:00',
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
        '/internal/v2/get-orders/list', json=etalon_request,
    )
    assert response.status_code == status
    if status == 200:
        json = response.json()
        assert json == etalon_response
