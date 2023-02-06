URL = '/eats/v1/eats-orders-tracking/v1/tracking-for-mobile/check'


async def test_fake_200(taxi_eats_orders_tracking, make_tracking_headers):
    response = await taxi_eats_orders_tracking.get(
        path=URL, headers=make_tracking_headers(eater_id='eater_id'),
    )
    assert response.status_code == 200
