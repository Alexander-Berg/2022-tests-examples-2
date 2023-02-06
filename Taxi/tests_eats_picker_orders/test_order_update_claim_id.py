async def test_order_update_claim_id_200(
        taxi_eats_picker_orders, create_order, get_order,
):
    order_id = create_order()
    eats_id = '123'
    new_claim_id = 'new_claim_id'

    response = await taxi_eats_picker_orders.put(
        f'api/v1/order/claim-id',
        json={'eats_id': eats_id, 'claim_id': new_claim_id},
    )
    assert response.status == 200
    assert get_order(order_id)['claim_id'] == new_claim_id


async def test_order_update_claim_id_404(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.put(
        f'api/v1/order/claim_id', json={'eats_id': 0, 'claim_id': 0},
    )
    assert response.status == 404
