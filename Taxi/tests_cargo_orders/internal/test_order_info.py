async def test_basic(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/internal/order/info', json={'order_id': 'taxi-order'},
    )
    assert response.status_code == 200
    assert response.json() == {'waybill_ref': 'waybill-ref'}


async def test_notfound(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/internal/order/info', json={'order_id': 'does not exist'},
    )
    assert response.status_code == 404
