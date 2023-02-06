import pytest


async def test_get_orders_format(
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

    response = await taxi_eats_picker_orders.get('/admin/v1/orders')
    assert response.status == 200

    expected_response = load_json('order_expected_response.json')
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
    assert response_data['orders'][0]['forwarded_courier_phone']
    del response_data['orders'][0]['forwarded_courier_phone']
    assert response_data['orders'][0]['forwarded_picker_phone']
    del response_data['orders'][0]['forwarded_picker_phone']
    assert expected_response['orders'][0] == response_data['orders'][0]


@pytest.mark.parametrize(
    'params, expected_status',
    [
        [{'created_from': '2022-07-05T11:00:00'}, 400],
        [{'created_to': '2022-07-05T11:00:00'}, 400],
    ],
)
async def test_get_orders_incorrect(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        params,
        expected_status,
):

    response = await taxi_eats_picker_orders.get(
        '/admin/v1/orders', params=params,
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'picker_ids, params, expected_orders',
    [
        [['1', '2'], {'picker_id': '2'}, ['2']],
        [['1', '2', '3', '4'], {'picker_id': '1'}, ['1']],
        [['1', '3', '4', '5'], {'picker_id': '2'}, []],
    ],
)
async def test_get_orders_by_picker_id(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        params,
        expected_orders,
        picker_ids,
):
    for index, picker_id in enumerate(picker_ids):
        eats_id = 'eats_id_' + str(index)
        create_order(
            eats_id=eats_id,
            picker_id=picker_id,
            last_version=100,
            state='picking',
        )

    response = await taxi_eats_picker_orders.get(
        '/admin/v1/orders', params=params,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == len(expected_orders)
    for index, order in enumerate(orders):
        assert expected_orders[index] == order['id']


@pytest.mark.parametrize(
    'eats_ids, params, expected_orders',
    [
        [['1', '2'], {'eats_id': '2'}, ['2']],
        [['1', '2', '3', '4'], {'eats_id': '1'}, ['1']],
        [['1', '3', '4', '5'], {'eats_id': '2'}, []],
    ],
)
async def test_get_orders_by_eats_id(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        params,
        expected_orders,
        eats_ids,
):
    for index, eats_id in enumerate(eats_ids):
        picker_id = 'picker_id_' + str(index)
        create_order(
            eats_id=eats_id,
            picker_id=picker_id,
            last_version=100,
            state='picking',
        )

    response = await taxi_eats_picker_orders.get(
        '/admin/v1/orders', params=params,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == len(expected_orders)
    for index, order in enumerate(orders):
        assert expected_orders[index] == order['id']


@pytest.mark.parametrize(
    'place_ids, params, expected_orders',
    [
        [['1', '2'], {'place_id': '2'}, ['2']],
        [['1', '2', '3', '4'], {'place_id': '1'}, ['1']],
        [['1', '3', '4', '5'], {'place_id': '2'}, []],
        [
            ['1', '2', '1', '3', '4', '2', '1'],
            {'place_id': '1'},
            ['1', '3', '7'],
        ],
    ],
)
async def test_get_orders_by_place_id(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        params,
        expected_orders,
        place_ids,
):
    for index, place_id in enumerate(place_ids):
        picker_id = 'picker_id_' + str(index)
        eats_id = 'eats_id_' + str(index)
        create_order(
            eats_id=eats_id,
            picker_id=picker_id,
            place_id=place_id,
            last_version=100,
            state='picking',
        )

    response = await taxi_eats_picker_orders.get(
        '/admin/v1/orders', params=params,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == len(expected_orders)
    for index, order in enumerate(orders):
        assert expected_orders[index] == order['id']


@pytest.mark.parametrize(
    'orders_created_at, params, expected_orders',
    [
        [
            [
                '2022-07-05T10:00:00+00:00',
                '2022-07-05T12:00:00+00:00',
                '2022-07-05T13:00:00+00:00',
            ],
            {'created_from': '2022-07-05T11:00:00+00:00'},
            ['2', '3'],
        ],
        [
            [
                '2022-07-05T10:00:00+00:00',
                '2022-07-05T12:00:00+00:00',
                '2022-07-05T13:00:00+00:00',
            ],
            {'created_from': '2022-07-05T12:00:00+00:00'},
            ['2', '3'],
        ],
        [
            [
                '2022-07-05T10:00:00+00:00',
                '2022-07-05T12:00:00+00:00',
                '2022-07-05T13:00:00+00:00',
            ],
            {'created_to': '2022-07-05T13:00:00+00:00'},
            ['1', '2', '3'],
        ],
        [
            [
                '2022-07-05T10:00:00+00:00',
                '2022-07-05T12:00:00+00:00',
                '2022-07-05T13:00:00+00:00',
            ],
            {'created_to': '2022-07-05T12:59:59+00:00'},
            ['1', '2'],
        ],
        [
            [
                '2022-07-05T10:00:00+00:00',
                '2022-07-05T12:00:00+00:00',
                '2022-07-05T13:00:00+00:00',
            ],
            {
                'created_from': '2022-07-05T10:00:01+00:00',
                'created_to': '2022-07-05T12:59:59+00:00',
            },
            ['2'],
        ],
        [
            [
                '2022-06-05T10:00:00+00:00',
                '2022-07-05T12:00:00+00:00',
                '2022-07-05T13:00:00+00:00',
            ],
            {
                'created_from': '2022-07-05T10:00:00+00:00',
                'created_to': '2022-07-05T13:00:00+00:00',
            },
            ['2', '3'],
        ],
        [
            [
                '2022-07-05T10:00:00+00:00',
                '2022-07-05T12:00:00+00:00',
                '2023-07-05T13:00:00+00:00',
            ],
            {
                'created_from': '2022-07-05T10:00:00+00:00',
                'created_to': '2022-07-05T13:00:00+00:00',
            },
            ['1', '2'],
        ],
        [
            [
                '2022-06-05T10:00:00+00:00',
                '2022-07-05T12:00:00+00:00',
                '2022-07-6T13:00:00+00:00',
            ],
            {
                'created_from': '2021-07-05T10:00:00+00:00',
                'created_to': '2022-07-05T13:00:00+00:00',
            },
            ['1', '2'],
        ],
    ],
)
async def test_get_orders_by_created_time(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        params,
        expected_orders,
        orders_created_at,
):
    for index, created_at in enumerate(orders_created_at):
        picker_id = 'picker_id_' + str(index)
        eats_id = 'eats_id_' + str(index)
        create_order(
            eats_id=eats_id,
            picker_id=picker_id,
            created_at=created_at,
            last_version=100,
            state='picking',
        )

    response = await taxi_eats_picker_orders.get(
        '/admin/v1/orders', params=params,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == len(expected_orders)
    for index, order in enumerate(orders):
        assert expected_orders[index] == order['id']


@pytest.mark.parametrize(
    'properties, params, expected_orders',
    [
        [
            [
                {
                    'picker_id': '1',
                    'eats_id': '1',
                    'created_at': '2022-07-05T10:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '2',
                    'created_at': '2022-07-05T10:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '3',
                    'created_at': '2022-07-05T10:00:00+00:00',
                },
                {
                    'picker_id': '1',
                    'eats_id': '4',
                    'created_at': '2022-07-05T12:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '5',
                    'created_at': '2022-07-05T12:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '6',
                    'created_at': '2022-07-05T12:00:00+00:00',
                },
                {
                    'picker_id': '1',
                    'eats_id': '7',
                    'created_at': '2022-07-05T13:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '8',
                    'created_at': '2022-07-05T13:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '9',
                    'created_at': '2022-07-05T13:00:00+00:00',
                },
            ],
            {'picker_id': '1', 'created_from': '2022-07-05T12:00:00+00:00'},
            ['4', '7'],
        ],
        [
            [
                {
                    'picker_id': '1',
                    'eats_id': '1',
                    'created_at': '2022-07-05T10:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '2',
                    'created_at': '2022-07-05T10:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '3',
                    'created_at': '2022-07-05T10:00:00+00:00',
                },
                {
                    'picker_id': '1',
                    'eats_id': '4',
                    'created_at': '2022-07-05T12:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '5',
                    'created_at': '2022-07-05T12:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '6',
                    'created_at': '2022-07-05T12:00:00+00:00',
                },
                {
                    'picker_id': '1',
                    'eats_id': '7',
                    'created_at': '2021-07-05T13:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '8',
                    'created_at': '2021-07-05T13:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '9',
                    'created_at': '2021-07-05T13:00:00+00:00',
                },
            ],
            {'picker_id': '3', 'created_from': '2022-07-05T10:00:00+00:00'},
            ['3', '6'],
        ],
        [
            [
                {
                    'picker_id': '1',
                    'eats_id': '1',
                    'created_at': '2022-07-05T10:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '2',
                    'created_at': '2022-07-05T10:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '3',
                    'created_at': '2022-07-05T10:00:00+00:00',
                },
                {
                    'picker_id': '1',
                    'eats_id': '4',
                    'created_at': '2022-07-05T12:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '5',
                    'created_at': '2022-07-05T12:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '6',
                    'created_at': '2022-07-05T12:00:00+00:00',
                },
                {
                    'picker_id': '1',
                    'eats_id': '7',
                    'created_at': '2022-07-05T13:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '8',
                    'created_at': '2022-07-05T13:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '9',
                    'created_at': '2022-07-05T13:00:00+00:00',
                },
            ],
            {'picker_id': '2', 'created_to': '2022-07-05T12:59:59+00:00'},
            ['2', '5'],
        ],
        [
            [
                {
                    'picker_id': '1',
                    'eats_id': '4',
                    'created_at': '2022-06-05T12:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '5',
                    'created_at': '2022-06-05T12:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '6',
                    'created_at': '2022-06-05T12:00:00+00:00',
                },
                {
                    'picker_id': '1',
                    'eats_id': '1',
                    'created_at': '2022-07-04T10:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '2',
                    'created_at': '2022-07-04T10:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '3',
                    'created_at': '2022-07-04T10:00:00+00:00',
                },
                {
                    'picker_id': '1',
                    'eats_id': '7',
                    'created_at': '2022-07-05T13:00:00+00:00',
                },
                {
                    'picker_id': '2',
                    'eats_id': '8',
                    'created_at': '2022-07-05T13:00:00+00:00',
                },
                {
                    'picker_id': '3',
                    'eats_id': '9',
                    'created_at': '2022-07-05T13:00:00+00:00',
                },
            ],
            {
                'picker_id': '1',
                'created_from': '2022-06-01T12:00:00+00:00',
                'created_to': '2022-07-05T12:59:59+00:00',
            },
            ['1', '4'],
        ],
    ],
)
async def test_get_orders_by_complex_filters(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        params,
        expected_orders,
        properties,
):
    for props in properties:
        eats_id = props['eats_id']
        picker_id = props['picker_id']
        created_at = props['created_at']
        create_order(
            eats_id=eats_id,
            picker_id=picker_id,
            created_at=created_at,
            last_version=100,
            state='complete',
        )

    response = await taxi_eats_picker_orders.get(
        '/admin/v1/orders', params=params,
    )
    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == len(expected_orders)
    for index, order in enumerate(orders):
        assert expected_orders[index] == order['id']
