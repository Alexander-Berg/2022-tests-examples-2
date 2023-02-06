URL = '/eats/v1/eats-orders-tracking/v1/abstract-bdu-action'


async def test_fake_200(taxi_eats_orders_tracking, make_tracking_headers):
    response = await taxi_eats_orders_tracking.post(
        path=URL,
        headers=make_tracking_headers(eater_id='eater_id'),
        json={'order_nr': 'success_order_nr', 'action_type': 'open_rover'},
    )
    assert response.status_code == 200
