import pytest


@pytest.mark.parametrize(
    'matrix_id,expected_status,expected_data,approve_author,'
    'is_approve_at_changed',
    [
        (1, 200, {}, 'Alice', True),
        (2, 200, {}, 'nevladov_test', False),
        (
            10,
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'10\' is not found',
            },
            '',
            False,
        ),
        (
            4,
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'4\' is not found',
            },
            '',
            False,
        ),
        (
            3,
            400,
            {
                'code': 'CANCEL_MATRIX_HAS_REASONS_DUPLICATES',
                'message': (
                    'Matrix with id 3 has duplicate cancellation reasons.'
                ),
                'details': {
                    'duplicate_reasons_names': [
                        ['Закрылся раньше', 'Закрылся намного раньше'],
                    ],
                    'matrix_id': 3,
                },
            },
            'Alice',
            True,
        ),
    ],
)
async def test_matrix_approve(
        taxi_eats_compensations_matrix,
        mockserver,
        matrix_id,
        expected_status,
        expected_data,
        approve_author,
        is_approve_at_changed,
        pgsql,
):
    def get_approve(matrix_id):
        pg_cursor = pgsql['eats_compensations_matrix'].cursor()
        pg_cursor.execute(
            f'SELECT approved_at AT TIME ZONE \'UTC\', approve_author '
            f'FROM eats_compensations_matrix.order_cancel_matrices '
            f'WHERE id = %s;',
            (matrix_id,),
        )
        approve = pg_cursor.fetchone()
        return approve

    approve_before = get_approve(matrix_id)

    response = await taxi_eats_compensations_matrix.put(
        'eats-compensations-matrix/v1/admin/cancel/matrix/approve',
        headers={'X-Yandex-Login': 'Alice'},
        params={'matrix_id': matrix_id},
    )
    assert response.status == expected_status
    if response.status != 200:
        data = response.json()
        assert data == expected_data
    else:
        approve_after = get_approve(matrix_id)
        assert approve_after[1] == approve_author
        assert is_approve_at_changed != (approve_after[0] == approve_before[0])
