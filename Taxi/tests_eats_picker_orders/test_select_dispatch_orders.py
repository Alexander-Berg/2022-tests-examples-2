import pytest


@pytest.mark.parametrize(
    'params, expected_eats_ids',
    [
        ({}, {'1234', '1235', '1236', '1237', '1238', '1239', '1240', '1241'}),
        ({'state': ['packing']}, {'1236', '1237'}),
        ({'flow_type': ['picking_only']}, {'1238', '1239', '1240'}),
        ({'has_picker': False}, {'1240', '1241'}),
        (
            {
                'state': ['complete'],
                'flow_type': ['picking_only'],
                'has_picker': False,
            },
            {'1240'},
        ),
        (
            {'state': ['picking', 'packing', 'complete']},
            {'1234', '1235', '1236', '1237', '1238', '1239', '1240', '1241'},
        ),
        (
            {'flow_type': ['picking_only', 'picking_packing']},
            {'1234', '1235', '1236', '1237', '1238', '1239', '1240', '1241'},
        ),
        (
            {
                'state': ['packing', 'complete'],
                'flow_type': ['picking_only', 'picking_packing'],
            },
            {'1236', '1237', '1239', '1240', '1241'},
        ),
    ],
)
async def test_select_dispatch_orders(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        params,
        expected_eats_ids,
):
    slot_start = '1976-01-19T15:00:27.010000+03:00'
    slot_end = '1976-01-19T15:00:27.010000+03:00'
    estimated_delivery_time = '1976-01-19T15:00:27.010000+03:00'
    region_id = 'region_id'
    create_order(
        eats_id='1234',
        picker_id='1',
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        slot_start=slot_start,
        slot_end=slot_end,
        estimated_delivery_time=estimated_delivery_time,
        region_id=region_id,
    )
    create_order(
        eats_id='1235',
        picker_id='2',
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        slot_start=slot_start,
        slot_end=slot_end,
        estimated_delivery_time=estimated_delivery_time,
        region_id=region_id,
    )
    create_order(
        eats_id='1236',
        picker_id='3',
        state='packing',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        slot_start=slot_start,
        slot_end=slot_end,
        estimated_delivery_time=estimated_delivery_time,
        region_id=region_id,
    )
    create_order(
        eats_id='1237',
        picker_id='4',
        state='packing',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        slot_start=slot_start,
        slot_end=slot_end,
        estimated_delivery_time=estimated_delivery_time,
        region_id=region_id,
    )
    create_order(
        eats_id='1238',
        picker_id='5',
        state='picking',
        payment_value=110,
        flow_type='picking_only',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        slot_start=slot_start,
        slot_end=slot_end,
        estimated_delivery_time=estimated_delivery_time,
        region_id=region_id,
    )
    create_order(
        eats_id='1239',
        picker_id='6',
        state='complete',
        payment_value=110,
        flow_type='picking_only',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        slot_start=slot_start,
        slot_end=slot_end,
        estimated_delivery_time=estimated_delivery_time,
        region_id=region_id,
    )
    create_order(
        eats_id='1240',
        picker_id=None,
        state='complete',
        payment_value=110,
        flow_type='picking_only',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        slot_start=slot_start,
        slot_end=slot_end,
        estimated_delivery_time=estimated_delivery_time,
        region_id=region_id,
    )
    create_order(
        eats_id='1241',
        picker_id=None,
        state='complete',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        slot_start=slot_start,
        slot_end=slot_end,
        estimated_delivery_time=estimated_delivery_time,
        region_id=region_id,
    )

    response = await taxi_eats_picker_orders.post(
        'api/v1/orders/select-for-dispatch', json=params,
    )

    assert response.status == 200
    assert {
        o['eats_id'] for o in response.json()['orders']
    } == expected_eats_ids
    assert {o['slot_start'] for o in response.json()['orders']} == {
        '1976-01-19T12:00:27.01+00:00',
    }
    assert {o['slot_end'] for o in response.json()['orders']} == {
        '1976-01-19T12:00:27.01+00:00',
    }
    assert {
        o['estimated_delivery_time'] for o in response.json()['orders']
    } == {'1976-01-19T12:00:27.01+00:00'}
    assert {o['region_id'] for o in response.json()['orders']} == {region_id}


@pytest.mark.parametrize(
    'has_original_items, author, author_type, expected_version',
    [
        [True, 'someone', None, 1],
        [True, 'customer', 'customer', 1],
        [True, '2', 'picker', 1],
        [True, '2', 'system', 1],
        [True, None, 'system', 1],
        [True, 'another_picker', 'picker', 0],
        [True, 'another_picker', 'system', 0],
        [False, 'another_picker', 'picker', 10],
        [False, 'another_picker', 'system', 10],
    ],
)
async def test_select_dispatch_orders_scheme(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        load_json,
        has_original_items,
        author,
        author_type,
        expected_version,
):
    order_id = create_order(
        eats_id='1234',
        picker_id='2',
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        last_version=10,
    )
    if has_original_items:
        create_order_item(
            order_id=order_id,
            eats_item_id='item-1',
            quantity=1,
            price=10,
            quantum_price=5,
            measure_value=1000,
            measure_quantum=500,
            quantum_quantity=2,
            absolute_quantity=1000,
            author=None,
            author_type=None,
            version=0,
        )

    create_order_item(
        order_id=order_id,
        eats_item_id='item-1',
        quantity=1,
        price=10,
        quantum_price=5,
        measure_value=1000,
        measure_quantum=500,
        quantum_quantity=2,
        absolute_quantity=1000,
        author=author,
        author_type=author_type,
        version=1,
    )

    response = await taxi_eats_picker_orders.post(
        'api/v1/orders/select-for-dispatch', json={},
    )
    assert response.status == 200

    expected_response = load_json('order_expected_response.json')
    expected_response['orders'][0]['version'] = expected_version
    response_data = response.json()
    assert response_data['orders'][0]['is_asap']
    del response_data['orders'][0]['is_asap']
    assert response_data['orders'][0]['status_updated_at']
    del response_data['orders'][0]['status_updated_at']
    assert response_data['orders'][0]['created_at']
    del response_data['orders'][0]['created_at']
    assert response_data['orders'][0]['updated_at']
    del response_data['orders'][0]['updated_at']
    assert expected_response == response_data
