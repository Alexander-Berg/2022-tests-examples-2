import pytest


@pytest.mark.parametrize(
    'matrix_id,version_code,expected_status,expected_data',
    [
        (
            1,
            'v.5.0',
            200,
            {
                'author': 'nevladov',
                'id': 5,
                'parent_version_code': 'v.1.0',
                'published': False,
                'version_code': 'v.5.0',
            },
        ),
        (2, 'v.5.0', 200, None),
        (3, 'v.5.0', 200, None),
        (4, 'v.5.0', 200, None),
        (
            None,
            'v.5.0',
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
            'v.5.0',
            404,
            {
                'code': 'MATRIX_IS_NOT_FOUND',
                'message': 'Matrix with id \'5\' is not found',
            },
        ),
        (
            1,
            'v.2.0',
            409,
            {
                'code': 'VERSION_CODE_IS_ALREADY_EXIST',
                'message': (
                    'Matrix with version code \'v.2.0\' is already exist'
                ),
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
            f'FROM eats_compensations_matrix.situations '
            f'WHERE matrix_id = %s;',
            (matrix_id,),
        )
        situation_ids = pg_cursor.fetchall()
        pg_cursor.execute(
            f'SELECT id '
            f'FROM eats_compensations_matrix.compensation_packs '
            f'WHERE situation_id = ANY(%s);',
            (situation_ids,),
        )
        pack_ids = pg_cursor.fetchall()
        pg_cursor.execute(
            f'SELECT id '
            f'FROM eats_compensations_matrix.compensation_packs_to_types '
            f'WHERE pack_id = ANY(%s);',
            (pack_ids,),
        )
        pack_to_type_link_ids = pg_cursor.fetchall()
        return (len(situation_ids), len(pack_ids), len(pack_to_type_link_ids))

    count_before = count(matrix_id)
    response = await taxi_eats_compensations_matrix.post(
        'eats-compensations-matrix/v1/admin/compensation/matrix/copy/',
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
