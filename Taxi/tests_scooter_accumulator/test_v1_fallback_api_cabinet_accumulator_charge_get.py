ENDPOINT = '/scooter-accumulator/v1/fallback-api/cabinet/accumulator/charge'


async def test_ok(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.get(
        ENDPOINT, params={'accumulator_id': 'accum_id1'},
    )

    assert response.status_code == 200
    assert response.json() == {'accumulator_charge': 95}


async def test_bad(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.get(
        ENDPOINT, params={'accumulator_id': 'accum_id_non_existent'},
    )

    assert response.status_code == 404
