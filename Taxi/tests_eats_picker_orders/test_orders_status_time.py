async def test_orders_status_time_200(
        taxi_eats_picker_orders, create_order, create_order_status,
):
    create_order(eats_id='1234', state='picking')
    create_order(eats_id='12345', state='picking')
    create_order(eats_id='123456', state='packing')
    create_order_status(order_id=1, last_version=1, state='packing')
    create_order_status(order_id=1, last_version=1, state='picking')
    create_order_status(order_id=1, last_version=1, state='packing')
    create_order_status(order_id=2, last_version=1, state='packing')
    create_order_status(order_id=2, last_version=1, state='picking')
    create_order_status(order_id=2, last_version=1, state='packing')

    response_with_first = await taxi_eats_picker_orders.post(
        '/api/v1/orders/status-time',
        json={
            'eats_ids': ['1234', '12345', '123456'],
            'state': 'picking',
            'sort': 'first',
        },
    )

    response_with_last = await taxi_eats_picker_orders.post(
        '/api/v1/orders/status-time',
        json={
            'eats_ids': ['1234', '12345', '123456'],
            'state': 'picking',
            'sort': 'last',
        },
    )

    assert response_with_first.status_code == 200
    assert response_with_last.status_code == 200
    assert len(response_with_first.json()['timestamps']) == 3
    assert len(response_with_last.json()['timestamps']) == 3
    assert (
        response_with_last.json()['timestamps'][0]['status_change_timestamp']
        > response_with_first.json()['timestamps'][0][
            'status_change_timestamp'
        ]
    )
    assert (
        response_with_last.json()['timestamps'][1]['status_change_timestamp']
        > response_with_first.json()['timestamps'][1][
            'status_change_timestamp'
        ]
    )
    assert (
        response_with_last.json()['timestamps'][2]['status_change_timestamp']
        == response_with_first.json()['timestamps'][2][
            'status_change_timestamp'
        ]
        is None
    )
    assert (
        response_with_last.json()['timestamps'][0]['eats_id']
        == response_with_first.json()['timestamps'][0]['eats_id']
        == '1234'
    )
    assert (
        response_with_last.json()['timestamps'][1]['eats_id']
        == response_with_first.json()['timestamps'][1]['eats_id']
        == '12345'
    )
    assert (
        response_with_last.json()['timestamps'][2]['eats_id']
        == response_with_first.json()['timestamps'][2]['eats_id']
        == '123456'
    )
