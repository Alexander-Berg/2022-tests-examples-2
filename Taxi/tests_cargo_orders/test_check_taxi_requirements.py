async def test_happy_path(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/v1/check-taxi-requirements',
        json={'taxi_classes': ['express', 'courier'], 'door_to_door': True},
    )
    assert response.status_code == 200


async def test_no_taxi_class(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/v1/check-taxi-requirements', json={'door_to_door': True},
    )
    assert response.status_code == 400


async def test_unknown_class(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/v1/check-taxi-requirements',
        json={'taxi_classes': ['unknown'], 'door_to_door': True},
    )
    assert response.status_code == 400


async def test_unknown_requirement(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        '/v1/check-taxi-requirements',
        json={'taxi_classes': ['express'], 'unknown': 123},
    )
    assert response.status_code == 400
