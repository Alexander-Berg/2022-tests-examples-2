async def test_retrieve_no_pricing(taxi_cargo_orders, order_id_no_pricing):
    response = await taxi_cargo_orders.post(
        '/v1/retrieve-pricing-data',
        json={'cargo_ref_id': f'order/{order_id_no_pricing}'},
    )
    assert response.status_code == 200
    assert response.json() == {}
