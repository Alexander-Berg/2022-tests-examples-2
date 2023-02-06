from tests_eats_pro_orders_bdu import models


@models.TIMER_CONFIG_ETA_TEXT
async def test_return(taxi_eats_pro_orders_bdu, default_order_id):
    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/return',
        headers=models.AUTH_HEADERS_V1,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'pickup_confirmation',
            'point_id': 1,
            'location_data': {'a': []},
            'comment': 'комент 1',
            'reasons': ['reason1', 'reason2'],
        },
    )

    assert response.status_code == 400
    assert (
        response.json()['message']
        == '/v1/cargo_ui/return handle is not supported'
    )
