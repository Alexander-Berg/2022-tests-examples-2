import pytest


@pytest.mark.parametrize(
    'matrix_id,expected_status,expected_data',
    [
        (1, 200, {}),
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
            100500,
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'100500\' is not found',
            },
        ),
        (
            5,
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'5\' is not editable cause'
                    ' it is already approved'
                ),
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
        pgsql,
):
    def get_deleted_at(matrix_id):
        pg_cursor = pgsql['eats_compensations_matrix'].cursor()
        pg_cursor.execute(
            f'SELECT deleted_at AT TIME ZONE \'UTC\' '
            f'FROM eats_compensations_matrix.order_cancel_matrices '
            f'WHERE id = %s;',
            (matrix_id,),
        )
        matrix = pg_cursor.fetchone()
        return matrix

    response = await taxi_eats_compensations_matrix.delete(
        'eats-compensations-matrix/v1/admin/cancel/matrix/',
        params={'matrix_id': matrix_id},
    )
    assert response.status == expected_status
    if response.status != 200:
        data = response.json()
        assert data == expected_data
    else:
        assert get_deleted_at(matrix_id)[0] is not None
