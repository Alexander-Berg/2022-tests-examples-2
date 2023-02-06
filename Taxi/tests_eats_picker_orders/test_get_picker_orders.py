import pytest

from . import utils

PARAMS = {'picker_id': '2'}
HEADERS = utils.da_headers('2')


def check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


@utils.polling_delay_config()
async def test_get_orders_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        load_json,
):
    order_id = create_order(
        eats_id='123',
        picker_id='1',
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        spent=None,
    )
    order_id2 = create_order(
        eats_id='1234',
        picker_id='2',
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        spent=None,
    )

    fst_order_item_id = create_order_item(
        order_id=order_id,
        quantity=1.5,
        measure_value=200,
        sold_by_weight=True,
        images=('https://example.org/product1/orig',),
        measure_quantum=150,
    )
    fst_order_item_id2 = create_order_item(
        order_id=order_id2,
        quantity=1.5,
        measure_value=200,
        sold_by_weight=True,
        images=('https://example.org/product1/orig',),
        measure_quantum=150,
    )
    create_picked_item(
        order_item_id=fst_order_item_id, picker_id='1', weight=150,
    )
    create_picked_item(
        order_item_id=fst_order_item_id2, picker_id='2', weight=150,
    )

    snd_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-124',
        category_id='13',
        category_name='Bread',
        barcode_weight_algorithm=None,
        quantity=5,
        measure_max_overweight=None,
        price=20,
        images=('https://example.org/product1/xxx.jpeg',),
        show_vendor_code=False,
        measure_quantum=0.75,
    )
    snd_order_item_id2 = create_order_item(
        order_id=order_id2,
        eats_item_id='eats-124',
        category_id='13',
        category_name='Bread',
        barcode_weight_algorithm=None,
        quantity=5,
        measure_max_overweight=None,
        price=20,
        images=('https://example.org/product1/xxx.jpeg',),
        show_vendor_code=False,
        measure_quantum=0.75,
    )

    create_picked_item(
        order_item_id=fst_order_item_id,
        picker_id='1',
        weight=150,
        cart_version=1,
    )
    create_picked_item(
        order_item_id=snd_order_item_id,
        picker_id='1',
        count=3,
        cart_version=1,
    )
    create_picked_item(
        order_item_id=fst_order_item_id2,
        picker_id='2',
        weight=150,
        cart_version=1,
    )
    create_picked_item(
        order_item_id=snd_order_item_id2,
        picker_id='2',
        count=3,
        cart_version=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders', headers=HEADERS,
    )
    assert response.status == 200
    assert response.headers['X-Polling-Delay'] == '30'
    check_polling_header(response.headers['X-Polling-Power-Policy'])

    expected_response = load_json('order_expected_response.json')
    expected_response['orders'][0]['id'] = str(order_id2)
    response_data = response.json()
    assert response_data['orders'][0]['is_asap']
    del response_data['orders'][0]['is_asap']
    assert response_data['orders'][0]['status_updated_at']
    del response_data['orders'][0]['status_updated_at']
    assert response_data['orders'][0]['created_at']
    del response_data['orders'][0]['created_at']
    assert response_data['orders'][0]['updated_at']
    del response_data['orders'][0]['updated_at']
    assert response_data['orders'][0]['customer_phone']
    del response_data['orders'][0]['customer_phone']
    assert response_data['orders'][0]['customer_picker_phone_forwarding']
    del response_data['orders'][0]['customer_picker_phone_forwarding']
    assert response_data['orders'][0]['payment_limit']
    del response_data['orders'][0]['payment_limit']
    assert response_data['orders'][0]['payment_limit_coefficient']
    del response_data['orders'][0]['payment_limit_coefficient']
    assert response_data['orders'][0]['held_payment_limit']
    del response_data['orders'][0]['held_payment_limit']
    assert expected_response == response_data

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders', headers=HEADERS,
    )
    assert response.status == 200
    assert response.headers['X-Polling-Delay'] == '30'
    check_polling_header(response.headers['X-Polling-Power-Policy'])

    expected_response = load_json('order_expected_response.json')
    expected_response['orders'][0]['id'] = str(order_id2)

    response_internal = await taxi_eats_picker_orders.get(
        '/api/v1/picker/orders', params=PARAMS,
    )
    expected_order = expected_response['orders'][0]
    expected_order['pickedup_total'] = None
    expected_order['total_weight'] = None
    del expected_order['forwarded_courier_phone']
    del expected_order['forwarded_picker_phone']
    assert response_internal.status == 200
    response_internal_data = response_internal.json()
    assert response_internal_data['orders'][0]['is_asap']
    del response_internal_data['orders'][0]['is_asap']
    assert response_internal_data['orders'][0]['status_updated_at']
    del response_internal_data['orders'][0]['status_updated_at']
    assert response_internal_data['orders'][0]['created_at']
    del response_internal_data['orders'][0]['created_at']
    assert response_internal_data['orders'][0]['updated_at']
    del response_internal_data['orders'][0]['updated_at']
    assert response_internal_data['orders'][0]['customer_phone']
    del response_internal_data['orders'][0]['customer_phone']
    assert response_internal_data['orders'][0]['forwarded_picker_phone']
    del response_internal_data['orders'][0]['forwarded_picker_phone']
    assert response_internal_data['orders'][0]['forwarded_courier_phone']
    del response_internal_data['orders'][0]['forwarded_courier_phone']
    assert response_internal_data['orders'][0][
        'customer_picker_phone_forwarding'
    ]
    del response_internal_data['orders'][0]['customer_picker_phone_forwarding']
    assert expected_response == response_internal_data


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker/api/v1/picker/orders', '/api/v1/picker/orders'],
)
@pytest.mark.parametrize(
    'last_version_author, last_version_author_type, expected_version, '
    'expected_items',
    [
        ['someone', None, 1, 2],
        ['2', 'picker', 1, 2],
        ['2', 'system', 1, 2],
        ['customer', 'customer', 1, 2],
        [None, 'system', 1, 2],
        ['another_picker', 'picker', 0, 1],
        ['another_picker', 'system', 0, 1],
    ],
)
async def test_get_orders_version_author_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        last_version_author,
        last_version_author_type,
        expected_version,
        expected_items,
        handle,
):
    picker_id = '2'
    eats_id = 'eats_id'
    eats_item_id_1 = 'eats_item_id_1'
    eats_item_id_2 = 'eats_item_id_2'
    order_id = create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        last_version=100,
        state='picking',
    )

    create_order_item(
        version=0,
        order_id=order_id,
        eats_item_id=eats_item_id_1,
        quantity=1,
        author='someone',
    )
    create_order_item(
        version=1,
        order_id=order_id,
        eats_item_id=eats_item_id_1,
        quantity=1,
        author=last_version_author,
        author_type=last_version_author_type,
    )
    create_order_item(
        version=1,
        order_id=order_id,
        eats_item_id=eats_item_id_2,
        quantity=2,
        author=last_version_author,
        author_type=last_version_author_type,
    )

    response = await taxi_eats_picker_orders.get(
        handle, headers=HEADERS, params=PARAMS,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['version'] == expected_version
    assert len(orders[0]['picker_items']) == expected_items


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker/api/v1/picker/orders', '/api/v1/picker/orders'],
)
@pytest.mark.parametrize('communication_policy', utils.COMMUNICATION_POLICIES)
@pytest.mark.parametrize(
    'not_found_item_policy', utils.NOT_FOUND_ITEM_POLICIES,
)
async def test_get_orders_picking_policies_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_picking_policy,
        handle,
        communication_policy,
        not_found_item_policy,
):
    eats_id = 'eats_id'
    picker_id = '2'
    create_order_picking_policy(
        eats_id=eats_id,
        communication_policy=communication_policy,
        not_found_item_policy=not_found_item_policy,
    )
    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        last_version=100,
        state='picking',
    )

    response = await taxi_eats_picker_orders.get(
        handle, headers=HEADERS, params=PARAMS,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['communication_policy'] == communication_policy
    assert orders[0]['not_found_item_policy'] == not_found_item_policy


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker/api/v1/picker/orders', '/api/v1/picker/orders'],
)
async def test_get_orders_picking_no_policies_200(
        taxi_eats_picker_orders, create_order, handle,
):
    eats_id = 'eats_id'
    picker_id = '2'
    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        last_version=100,
        state='picking',
    )

    response = await taxi_eats_picker_orders.get(
        handle, headers=HEADERS, params=PARAMS,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['communication_policy'] == utils.COMMUNICATION_POLICIES[0]
    assert (
        orders[0]['not_found_item_policy'] == utils.NOT_FOUND_ITEM_POLICIES[1]
    )


@utils.polling_delay_config()
async def test_get_orders_polling_delay_400(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders',
    )
    assert response.status == 400
    assert 'X-Polling-Delay' not in response.headers
    assert 'X-Polling-Power-Policy' not in response.headers


async def test_picker_assigned_count(
        taxi_eats_picker_orders, create_order, create_order_status,
):
    picker_id_1 = '1'
    picker_id_2 = '2'
    order_id1 = create_order(
        eats_id='123',
        picker_id=picker_id_1,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )
    order_id2 = create_order(
        eats_id='1234',
        picker_id=picker_id_2,
        state='new',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )
    create_order_status(
        order_id=order_id2,
        last_version=0,
        state='assigned',
        author_id=picker_id_2,
    )
    create_order_status(
        order_id=order_id2,
        last_version=0,
        state='assigned',
        author_id=picker_id_1,
    )
    create_order_status(
        order_id=order_id2,
        last_version=0,
        state='assigned',
        author_id=picker_id_2,
    )

    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='assigned',
        author_id=picker_id_1,
    )
    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='picking',
        author_id=picker_id_1,
    )
    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='assigned',
        author_id=picker_id_1,
    )
    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='assigned',
        author_id=picker_id_2,
    )
    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='assigned',
        author_id=picker_id_1,
    )

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders', headers=HEADERS,
    )
    assert response.status == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders',
        headers=utils.da_headers(picker_id_1),
    )
    assert response.status == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])


@pytest.mark.parametrize(
    'measure_version, pickedup_total',
    [[None, '67.50'], ['1', '67.50'], ['2', '52.50']],
)
@utils.polling_delay_config()
async def test_get_orders_measure_v2_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        load_json,
        measure_version,
        pickedup_total,
):
    order_id = create_order(
        eats_id='123',
        picker_id='1',
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        spent=None,
    )
    order_id2 = create_order(
        eats_id='1234',
        picker_id='2',
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        spent=None,
    )

    # новые поля не соответствуют старым, чтобы можно было увидеть разный
    # результат вычислений
    fst_order_item_id = create_order_item(
        order_id=order_id,
        quantity=1.5,
        measure_value=200,
        price=10,
        sold_by_weight=True,
        images=('https://example.org/product1/orig',),
        measure_quantum=100,
        quantum_quantity=2,
        absolute_quantity=200,
        quantum_price=15,
    )
    fst_order_item_id2 = create_order_item(
        order_id=order_id2,
        quantity=1.5,
        measure_value=200,
        price=10,
        sold_by_weight=True,
        images=('https://example.org/product1/orig',),
        measure_quantum=100,
        quantum_quantity=2,
        absolute_quantity=200,
        quantum_price=15,
    )
    create_picked_item(
        order_item_id=fst_order_item_id, picker_id='1', weight=150,
    )
    create_picked_item(
        order_item_id=fst_order_item_id2, picker_id='2', weight=150,
    )

    snd_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-124',
        category_id='13',
        category_name='Bread',
        barcode_weight_algorithm=None,
        quantity=5,
        measure_max_overweight=None,
        price=20,
        images=('https://example.org/product1/xxx.jpeg',),
        show_vendor_code=False,
        measure_quantum=100,
        quantum_quantity=1,
        absolute_quantity=100,
        quantum_price=10,
    )
    snd_order_item_id2 = create_order_item(
        order_id=order_id2,
        eats_item_id='eats-124',
        category_id='13',
        category_name='Bread',
        barcode_weight_algorithm=None,
        quantity=5,
        measure_max_overweight=None,
        price=20,
        images=('https://example.org/product1/xxx.jpeg',),
        show_vendor_code=False,
        measure_quantum=100,
        quantum_quantity=1,
        absolute_quantity=100,
        quantum_price=10,
    )

    create_picked_item(
        order_item_id=fst_order_item_id,
        picker_id='1',
        weight=150,
        cart_version=1,
    )
    create_picked_item(
        order_item_id=snd_order_item_id,
        picker_id='1',
        count=3,
        cart_version=1,
    )
    create_picked_item(
        order_item_id=fst_order_item_id2,
        picker_id='2',
        weight=150,
        cart_version=1,
    )
    create_picked_item(
        order_item_id=snd_order_item_id2,
        picker_id='2',
        count=3,
        cart_version=1,
    )

    headers = HEADERS
    if measure_version:
        headers['X-Measure-Version'] = measure_version
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/picker/orders',
        params=PARAMS,
        headers=headers,
    )
    assert response.status == 200
    assert response.headers['X-Polling-Delay'] == '30'
    check_polling_header(response.headers['X-Polling-Power-Policy'])

    expected_response = load_json('order_measure_v2_expected_response.json')
    expected_response['orders'][0]['id'] = str(order_id2)
    response_data = response.json()
    assert response_data['orders'][0]['is_asap']
    del response_data['orders'][0]['is_asap']
    assert response_data['orders'][0]['status_updated_at']
    del response_data['orders'][0]['status_updated_at']
    assert response_data['orders'][0]['created_at']
    del response_data['orders'][0]['created_at']
    assert response_data['orders'][0]['updated_at']
    del response_data['orders'][0]['updated_at']
    assert response_data['orders'][0]['customer_phone']
    del response_data['orders'][0]['customer_phone']
    assert response_data['orders'][0]['customer_picker_phone_forwarding']
    del response_data['orders'][0]['customer_picker_phone_forwarding']
    assert response_data['orders'][0]['payment_limit']
    del response_data['orders'][0]['payment_limit']
    assert response_data['orders'][0]['payment_limit_coefficient']
    del response_data['orders'][0]['payment_limit_coefficient']
    assert response_data['orders'][0]['pickedup_total'] == pickedup_total
    del response_data['orders'][0]['held_payment_limit']
    del response_data['orders'][0]['pickedup_total']
    assert expected_response == response_data

    response_internal = await taxi_eats_picker_orders.get(
        '/api/v1/picker/orders', params=PARAMS,
    )
    expected_order = expected_response['orders'][0]
    expected_order['pickedup_total'] = None
    expected_order['total_weight'] = None
    del expected_order['forwarded_courier_phone']
    del expected_order['forwarded_picker_phone']
    assert response_internal.status == 200
    response_internal_data = response_internal.json()
    assert response_internal_data['orders'][0]['is_asap']
    del response_internal_data['orders'][0]['is_asap']
    assert response_internal_data['orders'][0]['status_updated_at']
    del response_internal_data['orders'][0]['status_updated_at']
    assert response_internal_data['orders'][0]['created_at']
    del response_internal_data['orders'][0]['created_at']
    assert response_internal_data['orders'][0]['updated_at']
    del response_internal_data['orders'][0]['updated_at']
    assert response_internal_data['orders'][0]['customer_phone']
    del response_internal_data['orders'][0]['customer_phone']
    assert response_internal_data['orders'][0]['forwarded_picker_phone']
    del response_internal_data['orders'][0]['forwarded_picker_phone']
    assert response_internal_data['orders'][0]['forwarded_courier_phone']
    del response_internal_data['orders'][0]['forwarded_courier_phone']
    assert response_internal_data['orders'][0][
        'customer_picker_phone_forwarding'
    ]
    del response_internal_data['orders'][0]['customer_picker_phone_forwarding']
    assert expected_response == response_internal_data


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker/api/v1/picker/orders', '/api/v1/picker/orders'],
)
async def test_get_orders_customer_orders_count(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        handle,
):
    eats_id = 'eats_id'
    picker_id = '2'

    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        customer_orders_count=42,
    )

    response = await taxi_eats_picker_orders.get(
        handle, headers=HEADERS, params=PARAMS,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['customer_orders_count'] == 42


@pytest.mark.parametrize(
    'handle',
    ['/4.0/eats-picker/api/v1/picker/orders', '/api/v1/picker/orders'],
)
async def test_get_orders_orders_group_id(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        handle,
):
    eats_id = 'eats_id'
    picker_id = '2'
    orders_group_id = 'group_id'

    create_order(
        eats_id=eats_id, picker_id=picker_id, orders_group_id=orders_group_id,
    )

    response = await taxi_eats_picker_orders.get(
        handle, headers=HEADERS, params=PARAMS,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['orders_group_id'] == orders_group_id
