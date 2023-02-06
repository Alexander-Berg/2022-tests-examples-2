async def test_simple(taxi_scooters_misc):
    response = await taxi_scooters_misc.get(
        '/scooters-misc/v1/user-sessions',
        headers={'X-Yandex-UID': '4060779350'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'sessions': [{'scooter_id': '0b51b7fa-6d2d-a3b5-c5e4-4955c1645cf5'}],
    }
