async def test_passenger_ok(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'passenger',
        headers={
            'X-Yandex-Login': 'userx',
            'X-Login-Id': 'login_id_x',
            'X-Yandex-Uid': '100',
            'X-YaTaxi-Pass-Flags': 'phonish , portal,ya-plus',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'login': 'userx',
        'login_id': 'login_id_x',
        'yandex_uid': '100',
    }


async def test_passenger_invalid(taxi_userver_sample):
    response = await taxi_userver_sample.post('passenger')

    assert response.status_code == 200
    assert response.json() == {'special-field': 'not authorized'}
