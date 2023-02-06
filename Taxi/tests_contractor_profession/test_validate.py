async def test_ok(taxi_contractor_profession):
    response = await taxi_contractor_profession.post(
        '/internal/v1/professions/validate',
        params={'consumer': 'test_consumer'},
        json={'profession_id': 'taxi-driver'},
    )
    assert response.status_code == 200


async def test_fail(taxi_contractor_profession):
    response = await taxi_contractor_profession.post(
        '/internal/v1/professions/validate',
        params={'consumer': 'test_consumer'},
        json={'profession_id': 'invalid-profession-id'},
    )
    assert response.status_code == 400
