import pytest


@pytest.mark.pgsql('cargo_orders', files=['orders_errors.sql'])
@pytest.mark.parametrize(
    'waybill_ref, order_id',
    [
        ('waybill-ref', 'b1fe01dd-c302-4727-9f80-6e6c5e210a9f'),
        ('null-order-id', None),
    ],
)
async def test_error_info(taxi_cargo_orders, waybill_ref, order_id):
    response = await taxi_cargo_orders.post(
        '/v1/order/error-info', json={'waybill_ref': waybill_ref},
    )
    assert response.status_code == 200
    assert response.json()['order_error']['message'] == 'UNKNOWN_CARD'
    assert response.json()['order_error']['reason'] == 'COMMIT_ERROR'
    assert (
        response.json()['order_error']['updated_ts']
        == '2021-06-30T11:08:43.070017+00:00'
    )
    if order_id:
        assert response.json()['order_error']['cargo_order_id'] == order_id


async def test_no_error(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/v1/order/error-info', json={'waybill_ref': 'waybill-ref'},
    )
    assert response.status_code == 404
