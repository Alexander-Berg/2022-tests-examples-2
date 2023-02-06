import pytest


@pytest.mark.parametrize(
    'matrix_id,expected_status,expected_data',
    [
        (2, 200, None),
        (
            5,
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'5\' is not found',
            },
        ),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'matrix_id\' in query: None'
                ),
            },
        ),
    ],
)
async def test_matrix_approve(
        taxi_eats_compensations_matrix,
        mockserver,
        matrix_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.put(
        'eats-compensations-matrix/v1/admin/compensation/matrix/approve/',
        headers={'X-Yandex-Login': 'nevladov'},
        params={'matrix_id': matrix_id},
    )
    assert response.status == expected_status
    if expected_status != 200:
        data = response.json()
        assert data == expected_data
    else:
        response = await taxi_eats_compensations_matrix.get(
            'eats-compensations-matrix/v1/admin/compensation/matrix/',
            params={'matrix_id': matrix_id},
        )
        data = response.json()
        assert 'approved_at' in data
        assert data['approve_author'] == 'nevladov'
