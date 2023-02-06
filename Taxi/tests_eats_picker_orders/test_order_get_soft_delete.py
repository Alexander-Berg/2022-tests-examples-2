import pytest

from . import utils


@pytest.mark.parametrize(
    'handle, soft_deleted',
    [
        ['/4.0/eats-picker/api/v1/order', [False, True, False]],
        ['/api/v1/order', [False, True, False]],
    ],
)
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type',
    [
        ['1', 'picker'],
        ['1', None],
        ['system', 'system'],
        ['system', None],
        ['customer_id', 'customer'],
    ],
)
async def test_get_order_soft_deleted(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        handle,
        soft_deleted,
        is_deleted_by,
        deleted_by_type,
):
    eats_id = '123'
    picker_id = '1'
    order_id = create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        flow_type='picking_packing',
    )

    order_item_0 = create_order_item(
        order_id=order_id, eats_item_id='eats-item-0', measure_value=100,
    )

    order_item_1 = create_order_item(
        order_id=order_id,
        eats_item_id='eats-item-1',
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
        measure_value=100,
    )

    order_item_2 = create_order_item(
        order_id=order_id,
        eats_item_id='eats-item-2',
        is_deleted_by='unknown_picker_id',
        measure_value=100,
    )

    for order_item_id in [order_item_0, order_item_1, order_item_2]:
        create_picked_item(
            order_item_id=order_item_id, picker_id=picker_id, count=1,
        )

    response = await taxi_eats_picker_orders.get(
        handle,
        params={'eats_id': eats_id, 'version': 0},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    response_data = response.json()
    for i in [0, 1, 2]:
        assert (
            response_data['payload']['picker_items'][i]['soft_deleted']
            == soft_deleted[i]
        )
