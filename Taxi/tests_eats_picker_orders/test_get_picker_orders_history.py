import decimal


import pytest


from . import utils


async def test_get_picker_orders_history_400(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders/history',
    )
    assert response.status == 400


@pytest.mark.experiments3(filename='config3_picker_orders_history.json')
@pytest.mark.now('2021-06-16T00:00:00+0000')
@pytest.mark.parametrize(
    'picker_id, date_from, date_to, expected_orders',
    [
        (
            'picker_0',
            '2021-06-01T00:00:00+0000',
            '2021-06-16T00:00:00+0000',
            [3, 4],
        ),
        ('picker_0', '2021-06-01T00:00:00+0000', None, [3, 4]),
        ('picker_0', None, '2021-06-16T00:00:00+0000', [3, 4]),
        ('picker_0', None, None, [3, 4]),
        (
            'picker_1',
            '2021-06-01T00:00:00+0000',
            '2021-06-16T00:00:00+0000',
            [5, 6],
        ),
        ('picker_1', '2021-06-01T00:00:00+0000', None, [5, 6]),
        ('picker_1', None, '2021-06-16T00:00:00+0000', [5, 6]),
        ('picker_1', None, None, [5, 6]),
        (
            'picker_0',
            '2021-06-01T00:00:00+0000',
            '2021-06-03T00:00:00+0000',
            [0, 1],
        ),
        (
            'picker_0',
            '2021-06-01T00:00:00+0000',
            '2021-06-02T00:00:00+0000',
            [0],
        ),
        (
            'picker_1',
            '2021-06-01T00:00:00+0000',
            '2021-06-03T00:00:00+0000',
            [],
        ),
        ('picker_2', None, None, [7, 8, 9]),
    ],
)
async def test_get_picker_orders_history_200(
        taxi_eats_picker_orders,
        load_json,
        create_order,
        now,
        picker_id,
        date_from,
        date_to,
        expected_orders,
):
    orders = load_json('orders.json')['orders']
    for order in orders:
        create_order(
            eats_id=order['eats_id'],
            picker_id=order['picker_id'],
            created_at=order['created_at'],
            state=order.get('state'),
            cargo_order_status=order.get('cargo_order_status'),
            courier_name=order.get('courier_name'),
            courier_phone=(
                (order['forwarded_courier_phone'], now)
                if 'forwarded_courier_phone' in order
                else None
            ),
            customer_forwarded_phone=(
                (
                    order['customer_forwarded_phone']['phone'],
                    order['customer_forwarded_phone']['expired_at'],
                )
                if 'customer_forwarded_phone' in order
                else None
            ),
            courier_pickup_expected_at=order.get('courier_pickup_expected_at'),
            courier_delivery_expected_at=order.get(
                'courier_delivery_expected_at',
            ),
            courier_location=order.get('courier_location'),
        )

    params = {'picker_id': picker_id}
    if date_from:
        params['from'] = date_from
    if date_to:
        params['to'] = date_to
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders/history',
        params=params,
        headers=utils.da_headers(picker_id),
    )

    assert response.status == 200
    expected_orders = [orders[i] for i in expected_orders]
    for order in expected_orders:
        if 'customer_forwarded_phone' in order:
            order['customer_forwarded_phone'] = order[
                'customer_forwarded_phone'
            ]['phone']
        del order['picker_id']
        del order['created_at']
        if 'spent' in order:
            del order['spent']
        order['items_count'] = 0
    result_orders = response.json()['orders']
    for order in result_orders:
        if 'spent' in order:
            del order['spent']
    assert result_orders == expected_orders


@pytest.mark.experiments3(filename='config3_picker_orders_history.json')
@pytest.mark.now('2021-07-20T16:00:00+0000')
@pytest.mark.parametrize(
    'eats_order_id, price1, price2, spent, phone_expired_at, phone_returned',
    [
        ('eats_id1', 100.50, 150.90, 300, '2021-07-20T17:50:00+0000', True),
        ('eats_id2', 123.99, 11, 150, '2021-07-20T15:50:00+0000', False),
    ],
)
async def test_get_picker_orders_history_new_fields(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order_item,
        create_order,
        create_picked_item,
        eats_order_id,
        price1,
        price2,
        spent,
        phone_expired_at,
        phone_returned,
):

    picker_id = 'picker_id'
    customer_phone = '+7-call-me-customer'

    order = create_order(
        eats_id=eats_order_id,
        picker_id=picker_id,
        created_at='2021-07-18T16:00:00+0000',
        state='complete',
        cargo_order_status='new',
        customer_forwarded_phone=(customer_phone, phone_expired_at),
        spent=spent,
    )

    item1 = create_order_item(
        order_id=order, eats_item_id='eats1', price=price1,
    )
    item2 = create_order_item(
        order_id=order, eats_item_id='eats2', price=price2,
    )

    create_picked_item(
        order_item_id=item1, picker_id=picker_id, cart_version=0, count=1,
    )
    create_picked_item(
        order_item_id=item2, picker_id=picker_id, cart_version=0, count=1,
    )

    params = {
        'picker_id': picker_id,
        'from': '2021-07-17T16:00:00+0000',
        'to': '2021-07-20T16:00:00+0000',
    }
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders/history',
        params=params,
        headers=utils.da_headers(picker_id),
    )

    assert response.status == 200
    result = response.json()['orders'][0]
    assert result['eats_id'] == eats_order_id
    if phone_returned:
        assert result['customer_forwarded_phone'] == customer_phone
    else:
        assert 'customer_forwarded_phone' not in result
    assert decimal.Decimal(result['pickedup_total']) == round(
        decimal.Decimal(price1 + price2), 2,
    )
    assert decimal.Decimal(result['spent']) == decimal.Decimal(spent)
    assert result['original_items_count'] == 2


@pytest.mark.experiments3(filename='config3_picker_orders_history.json')
@pytest.mark.now('2021-07-20T16:00:00+0000')
async def test_get_picker_orders_history_pickedup_total(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    customer_phone = '+7-call-me-customer'

    order = create_order(
        eats_id='eats_order_id',
        picker_id=picker_id,
        created_at='2021-07-18T16:00:00+0000',
        state='complete',
        cargo_order_status='new',
        customer_forwarded_phone=(customer_phone, '2021-07-20T17:50:00+0000'),
        spent=1234.55,
    )

    item1 = create_order_item(
        order_id=order, eats_item_id='eats1', price=123.45,
    )
    item2 = create_order_item(
        order_id=order, eats_item_id='eats2', price=678.90,
    )

    create_picked_item(
        order_item_id=item1, picker_id=picker_id, cart_version=0, count=1,
    )
    create_picked_item(
        order_item_id=item2, picker_id=picker_id, cart_version=0, count=1,
    )

    params = {
        'picker_id': picker_id,
        'from': '2021-07-17T16:00:00+0000',
        'to': '2021-07-20T16:00:00+0000',
    }
    history_response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders/history',
        params=params,
        headers=utils.da_headers(picker_id),
    )

    assert history_response.status == 200
    history_orders = history_response.json()['orders']
    assert len(history_orders) == 1

    get_order_response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': 'eats_order_id'},
        headers=utils.da_headers(picker_id),
    )
    assert get_order_response.status == 200
    get_order_orders = get_order_response.json()['payload']
    assert (
        history_orders[0]['pickedup_total']
        == get_order_orders['pickedup_total']
    )
    assert history_orders[0]['original_items_count'] == 2


@pytest.mark.experiments3(filename='config3_picker_orders_history.json')
@utils.polling_delay_config()
@pytest.mark.now('2021-07-20T16:00:00+0000')
async def test_get_picker_orders_history_polling_delay_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    customer_phone = '+7-call-me-customer'

    order = create_order(
        eats_id='eats_order_id',
        picker_id=picker_id,
        created_at='2021-07-18T16:00:00+0000',
        state='complete',
        cargo_order_status='new',
        customer_forwarded_phone=(customer_phone, '2021-07-20T17:50:00+0000'),
        spent=1234.55,
    )

    item1 = create_order_item(
        order_id=order, eats_item_id='eats1', price=123.45,
    )
    item2 = create_order_item(
        order_id=order, eats_item_id='eats2', price=678.90,
    )

    create_picked_item(
        order_item_id=item1, picker_id=picker_id, cart_version=0, count=1,
    )
    create_picked_item(
        order_item_id=item2, picker_id=picker_id, cart_version=0, count=1,
    )

    params = {
        'picker_id': picker_id,
        'from': '2021-07-17T16:00:00+0000',
        'to': '2021-07-20T16:00:00+0000',
    }
    history_response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders/history',
        params=params,
        headers=utils.da_headers(picker_id),
    )

    assert history_response.status == 200
    assert history_response.headers['X-Polling-Delay'] == '120'
    assert (
        history_response.headers['X-Polling-Config']
        == 'picking=45s,auto_handle=3s,manual_handle=20s'
    )
    assert history_response.json()['orders'][0]['original_items_count'] == 2


@pytest.mark.experiments3(filename='config3_picker_orders_history.json')
@utils.polling_delay_config()
async def test_get_picker_orders_history_polling_delay_400(
        taxi_eats_picker_orders,
):
    history_response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders/history',
    )

    assert history_response.status == 400
    assert 'X-Polling-Delay' not in history_response.headers
    assert 'X-Polling-Config' not in history_response.headers


@pytest.mark.experiments3(filename='config3_picker_orders_history.json')
@pytest.mark.now('2021-08-20T12:00:00+0000')
@pytest.mark.parametrize(
    'last_version_author, last_version_author_type, pickedup_total',
    [
        ['someone', None, '400.00'],
        ['picker_id', 'picker', '400.00'],
        ['picker_id', 'system', '400.00'],
        ['customer', 'customer', '400.00'],
        [None, 'system', '400.00'],
        ['another_picker', 'picker', '100.00'],
        ['another_picker', 'system', '100.00'],
    ],
)
async def test_get_picker_orders_history_version_author_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        last_version_author,
        last_version_author_type,
        pickedup_total,
):
    eats_id = 'eats_id'
    picker_id = 'picker_id'
    eats_item_id_1 = 'eats_item_id_1'
    eats_item_id_2 = 'eats_item_id_2'
    order_id = create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        last_version=100,
        state='complete',
        cargo_order_status='new',
        created_at='2021-08-20T11:00:00+0000',
    )

    item_id_1 = create_order_item(
        version=0,
        order_id=order_id,
        eats_item_id=eats_item_id_1,
        quantity=1,
        price=100,
    )
    item_id_2 = create_order_item(
        version=1,
        order_id=order_id,
        eats_item_id=eats_item_id_2,
        quantity=2,
        price=200,
        author=last_version_author,
        author_type=last_version_author_type,
        replacements=[(eats_item_id_1, item_id_1)],
    )
    create_picked_item(order_item_id=item_id_1, picker_id=picker_id, count=1)
    create_picked_item(order_item_id=item_id_2, picker_id=picker_id, count=2)
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders/history',
        headers=utils.da_headers(picker_id),
    )

    assert response.status == 200
    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['eats_id'] == eats_id
    assert orders[0]['pickedup_total'] == pickedup_total
