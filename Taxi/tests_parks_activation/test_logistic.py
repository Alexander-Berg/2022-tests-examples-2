async def test_cargo_service(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        '/parks/activation/cargo-service', params={'park_id': '100'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_cargo_service': True,
        'has_cargo_corp_service': False,
        'country': 'rus',
    }


async def test_cargo_service_unknown_park(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        '/parks/activation/cargo-service',
        params={'park_id': 'some_unknown_park'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_cargo_service': False,
        'has_cargo_corp_service': False,
    }


async def test_cargo_service_dry(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        '/parks/activation/cargo-service',
        params={'park_id': '100', 'due': '2022-02-22T10:00:00+0000'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_cargo_service': True,
        'has_cargo_corp_service': False,
        'country': 'rus',
    }


async def test_cargo_service_unknown_park_dry(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        '/parks/activation/cargo-service',
        params={'park_id': 'some_unknown_park'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_cargo_service': False,
        'has_cargo_corp_service': False,
    }


async def test_cargo_service_new(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        '/parks/activation/cargo-service', params={'park_id': '100'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_cargo_service': True,
        'has_cargo_corp_service': False,
        'country': 'rus',
    }


async def test_cargo_service_unknown_park_new(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        '/parks/activation/cargo-service',
        params={'park_id': 'some_unknown_park'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_cargo_service': False,
        'has_cargo_corp_service': False,
    }


async def test_cargo_service_with_due_new(taxi_parks_activation):
    response = await taxi_parks_activation.post(
        '/parks/activation/cargo-service',
        params={'park_id': '400', 'due': '2022-02-18T00:00:00+0000'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'has_cargo_service': True,
        'has_cargo_corp_service': False,
        'country': 'rus',
    }
