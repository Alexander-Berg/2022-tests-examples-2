import pytest

PICKER_ID = '2'


@pytest.mark.parametrize(
    'has_original_items, author, author_type, expected_version',
    [
        [True, 'someone', None, 1],
        [True, 'customer', 'customer', 1],
        [True, PICKER_ID, 'picker', 1],
        [True, PICKER_ID, 'system', 1],
        [True, None, 'system', 1],
        [True, 'another_picker', 'picker', 0],
        [True, 'another_picker', 'system', 0],
        [False, 'another_picker', 'picker', 10],
        [False, 'another_picker', 'system', 10],
    ],
)
async def test_get_orders(
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
    response = await taxi_eats_picker_orders.get('/api/v1/orders')
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
