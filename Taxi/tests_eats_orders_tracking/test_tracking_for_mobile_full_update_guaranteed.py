URL = (
    '/eats/v1/eats-orders-tracking/v1/tracking-for-mobile'
    '/full-update-guaranteed'
)


async def test_fake_200(taxi_eats_orders_tracking, make_tracking_headers):
    response = await taxi_eats_orders_tracking.get(
        path=URL,
        headers=make_tracking_headers(eater_id='eater_id'),
        params={'order_nr': 'some_order_nr'},
    )
    assert response.status_code == 200


async def test_fake_404(taxi_eats_orders_tracking, make_tracking_headers):
    response = await taxi_eats_orders_tracking.get(
        path=URL,
        headers=make_tracking_headers(eater_id='eater_id'),
        params={'order_nr': 'non_existent_order_nr'},
    )
    assert response.status_code == 404
