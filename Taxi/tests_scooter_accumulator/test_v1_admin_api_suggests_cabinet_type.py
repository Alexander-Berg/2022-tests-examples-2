ENDPOINT = '/scooter-accumulator/v1/admin-api/suggests/cabinet/type'

RESPONSE = {
    'cabinet_types': [
        'cabinet',
        'cabinet_without_validation',
        'charge_station',
        'charge_station_without_id_receiver',
    ],
}


async def test_ok(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.get(ENDPOINT)

    assert response.status_code == 200
    assert response.json() == RESPONSE
