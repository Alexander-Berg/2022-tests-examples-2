import pytest


@pytest.mark.parametrize('state', ['picking'])
async def test_get_estimation_orders(
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        taxi_eats_picker_orders,
        state,
):
    orders_count = 5

    place_id = 123
    brand_id = 'brand-id'
    flow_type = 'picking_only'
    orders = [
        {
            'eats_id': f'eats-{i}',
            'place_id': place_id,
            'brand_id': brand_id,
            'flow_type': flow_type,
            'picker_id': f'picker-{i}',
            'state': state,
        }
        for i in range(orders_count)
    ]

    category_id = 'category-id'
    order_items = [
        {
            'category_id': category_id,
            'eats_item_id': 'РН000001',
            'sold_by_weight': True,
        },
        {
            'category_id': category_id,
            'eats_item_id': 'РН000002',
            'sold_by_weight': False,
            'quantity': 3,
        },
    ]
    picked_items = {
        'РН000001': {'cart_version': '0', 'weight': 500, 'count': None},
        'РН000002': {'cart_version': '0', 'weight': None, 'count': 3},
    }

    for order in orders:
        order_id = create_order(**order)
        for order_item in order_items:
            order_item_id = create_order_item(order_id=order_id, **order_item)
            if order_item['eats_item_id'] in picked_items:
                create_picked_item(
                    order_item_id=order_item_id,
                    eats_item_id=order_item['eats_item_id'],
                    picker_id=order['picker_id'],
                    **picked_items[order_item['eats_item_id']],
                )

    response = await taxi_eats_picker_orders.post(
        'api/v1/estimation-orders',
        json={'eats_ids': [order['eats_id'] for order in orders]},
    )
    assert response.status_code == 200
    assert len(response.json()['estimation_orders']) == orders_count
    for estimation_order in response.json()['estimation_orders']:
        assert estimation_order['eats_id'] in set(
            order['eats_id'] for order in orders
        )
        assert estimation_order['place_id'] == place_id
        assert estimation_order['brand_id'] == brand_id
        assert estimation_order['flow_type'] == flow_type
        assert estimation_order['items'] == [
            {
                'category_id': item['category_id'],
                'is_catch_weight': item['sold_by_weight'],
                'count': None if item['sold_by_weight'] else item['quantity'],
            }
            for item in order_items
        ]
        assert estimation_order['picked_items'] == [
            {'id': id, 'weight': item['weight'], 'count': item['count']}
            for id, item in picked_items.items()
        ]
