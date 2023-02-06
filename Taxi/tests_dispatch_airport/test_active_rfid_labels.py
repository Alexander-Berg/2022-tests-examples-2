from tests_dispatch_airport import common


async def test_active_rfid_labels(taxi_dispatch_airport, load_json):
    response = await taxi_dispatch_airport.get(
        '/internal/active-rfid-labels',
        headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
    )
    assert response.status_code == 200
    r_json = sorted(response.json(), key=lambda x: x['car_number'])
    assert r_json == load_json('cache_etalon.json')
