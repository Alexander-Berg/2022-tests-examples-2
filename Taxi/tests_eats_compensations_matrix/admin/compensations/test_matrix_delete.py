import pytest


@pytest.mark.parametrize(
    'matrix_id,expected_status,expected_data',
    [
        (4, 200, None),
        (2, 200, None),
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
        (
            3,
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'3\' is not editable cause it is '
                    'already approved'
                ),
            },
        ),
        (
            5,
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'5\' is not found',
            },
        ),
    ],
)
async def test_matrix_delete(
        taxi_eats_compensations_matrix,
        mockserver,
        matrix_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.delete(
        'eats-compensations-matrix/v1/admin/compensation/matrix/',
        params={'matrix_id': matrix_id},
    )
    assert response.status == expected_status
    if expected_status != 200:
        data = response.json()
        assert data == expected_data
