import pytest


@pytest.mark.parametrize(
    'matrix_id,version_code,expected_status,expected_data',
    [
        (
            1,
            'cancel_v.10.0',
            200,
            {
                'author': 'nevladov',
                'id': 6,
                'parent_version_code': 'cancel_v.1.0',
                'published': False,
                'version_code': 'cancel_v.10.0',
            },
        ),
        (2, 'cancel_v.10.0', 200, None),
        (3, 'cancel_v.10.0', 200, None),
        (
            None,
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
            None,
            'cancel_v.10.0',
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
            'cancel_v.10.0',
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'10\' is not found',
            },
        ),
        (
            1,
            'cancel_v.1.0',
            409,
            {
                'code': 'VERSION_CODE_IS_ALREADY_EXIST',
                'message': (
                    'Matrix with version code \'cancel_v.1.0\' is already '
                    'exist'
                ),
            },
        ),
        (
            4,
            'cancel_v.10.0',
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'4\' is not found',
            },
        ),
    ],
)
async def test_matrix_copy(
        taxi_eats_compensations_matrix,
        mockserver,
        pgsql,
        matrix_id,
        version_code,
        expected_status,
        expected_data,
):
    def count(matrix_id):
        pg_cursor = pgsql['eats_compensations_matrix'].cursor()
        pg_cursor.execute(
            f'SELECT id '
            f'FROM eats_compensations_matrix.order_cancel_reasons '
            f'WHERE matrix_id = %s AND deleted_at IS NULL;',
            (matrix_id,),
        )
        reasons_ids = pg_cursor.fetchall()
        pg_cursor.execute(
            f'SELECT reaction_id '
            f'FROM eats_compensations_matrix.order_cancel_reasons_reactions '
            f'WHERE reason_id = ANY(%s) AND deleted_at IS NULL;',
            (reasons_ids,),
        )
        reactions_ids = pg_cursor.fetchall()
        return (len(reasons_ids), len(reactions_ids))

    count_before = count(matrix_id)
    response = await taxi_eats_compensations_matrix.post(
        'eats-compensations-matrix/v1/admin/cancel/matrix/copy/',
        params={'matrix_id': matrix_id, 'version_code': version_code},
        headers={'X-Yandex-Login': 'nevladov'},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        new_matrix_id = data['id']
        assert new_matrix_id != matrix_id
        count_after = count(new_matrix_id)
        assert count_before == count_after
        data.pop('created_at')
        data.pop('updated_at')
    if expected_data is not None:
        assert data == expected_data
