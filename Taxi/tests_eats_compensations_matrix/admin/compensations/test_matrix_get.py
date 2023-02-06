import pytest


@pytest.mark.parametrize(
    'matrix_id,expected_status,expected_data',
    [
        (
            1,
            200,
            {
                'id': 1,
                'version_code': 'v.1.0',
                'parent_version_code': '',
                'approved_at': '2020-06-09T11:00:00+00:00',
                'author': 'nevladov',
                'approve_author': 'nevladov',
                'created_at': '2020-06-09T10:00:00+00:00',
                'updated_at': '2020-06-09T09:00:00+00:00',
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
            5,
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'5\' is not found',
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
        'eats-compensations-matrix/v1/admin/compensation/matrix/',
        params={'matrix_id': matrix_id},
    )
    assert response.status == expected_status
    data = response.json()
    assert data == expected_data
