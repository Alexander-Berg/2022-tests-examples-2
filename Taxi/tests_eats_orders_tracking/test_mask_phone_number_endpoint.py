URL = '/eats/v1/eats-orders-tracking/v1/mask-phone-number'


async def test_fake_200(taxi_eats_orders_tracking, make_tracking_headers):
    response = await taxi_eats_orders_tracking.post(
        path=URL,
        headers=make_tracking_headers(eater_id='eater_id'),
        json={'order_nr': 'success_order_nr', 'contact_type': 'courier'},
    )
    assert response.status_code == 200


async def test_fake_400(taxi_eats_orders_tracking, make_tracking_headers):
    response = await taxi_eats_orders_tracking.post(
        path=URL,
        headers=make_tracking_headers(eater_id='eater_id'),
        json={'order_nr': 'failed_order_nr', 'contact_type': 'courier'},
    )
    assert response.status_code == 400
