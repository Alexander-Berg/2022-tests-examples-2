async def test_204(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        '/v1/partners/nomenclature/stock?place_id=99999', json={},
    )

    assert response.status == 204
