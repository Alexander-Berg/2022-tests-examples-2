async def test_get_csv(taxi_eats_compensations_matrix, mockserver, load):
    response = await taxi_eats_compensations_matrix.get(
        'eats-compensations-matrix/v1/admin/compensation/generate_csv/',
        params={'matrix_id': 1},
    )

    assert response.status == 200
    assert response.text == load('expected_response.csv')
