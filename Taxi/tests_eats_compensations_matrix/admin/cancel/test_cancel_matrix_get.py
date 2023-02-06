import pytest


@pytest.mark.parametrize(
    'matrix_id,expected_status,expected_data',
    [
        (
            1,
            200,
            {
                'id': 1,
                'version_code': 'cancel_v.1.0',
                'author': 'nevladov',
                'created_at': '2020-06-23T08:00:00+00:00',
                'updated_at': '2020-06-23T08:00:00+00:00',
                'published': False,
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
        (
            10,
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'10\' is not found',
            },
        ),
        (
            4,
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'4\' is not found',
            },
        ),
    ],
)
async def test_matrix_get(
        taxi_eats_compensations_matrix,
        mockserver,
        matrix_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.get(
        'eats-compensations-matrix/v1/admin/cancel/matrix/',
        params={'matrix_id': matrix_id},
    )
    assert response.status == expected_status
    data = response.json()
    assert data == expected_data
