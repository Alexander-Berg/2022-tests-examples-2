import pytest


@pytest.mark.parametrize(
    'situation_id,expected_status,expected_data',
    [
        (
            3,
            200,
            {
                'id': 6,
                'matrix_id': 2,
                'group_id': 2,
                'code': 'long_delay',
                'title': 'более 30 минут',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 98,
                'is_system': False,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': [
                    'marketplace',
                    'our_delivery',
                    'pickup',
                ],
                'is_available_before_final_status': False,
            },
        ),
        (
            5,
            200,
            {
                'id': 6,
                'matrix_id': 4,
                'group_id': 2,
                'code': 'long_delay',
                'title': 'более 30 минут',
                'violation_level': 'low',
                'responsible': 'company',
                'need_confirmation': False,
                'priority': 98,
                'is_system': False,
                'order_type': ['native', 'lavka'],
                'order_delivery_type': [
                    'marketplace',
                    'our_delivery',
                    'pickup',
                ],
                'is_available_before_final_status': True,
            },
        ),
        (4, 200, None),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'situation_id\' '
                    'in query: None'
                ),
            },
        ),
        (
            1,
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'1\' is not editable cause it is '
                    'already approved'
                ),
            },
        ),
        (
            10,
            404,
            {
                'code': 'SITUATION_IS_NOT_FOUND',
                'message': 'Situation with id \'10\' is not found',
            },
        ),
    ],
)
async def test_situation_copy(
        taxi_eats_compensations_matrix,
        mockserver,
        pgsql,
        situation_id,
        expected_status,
        expected_data,
):
    def count(situation_id):
        pg_cursor = pgsql['eats_compensations_matrix'].cursor()
        pg_cursor.execute(
            f'SELECT id '
            f'FROM eats_compensations_matrix.compensation_packs '
            f'WHERE situation_id = %s;',
            (situation_id,),
        )
        pack_ids = pg_cursor.fetchall()
        pg_cursor.execute(
            f'SELECT id '
            f'FROM eats_compensations_matrix.compensation_packs_to_types '
            f'WHERE pack_id = ANY(%s);',
            (pack_ids,),
        )
        pack_to_type_link_ids = pg_cursor.fetchall()
        return (len(pack_ids), len(pack_to_type_link_ids))

    count_before = count(situation_id)
    response = await taxi_eats_compensations_matrix.post(
        'eats-compensations-matrix/v1/admin/compensation/situation/copy/',
        params={'situation_id': situation_id},
        headers={'X-Yandex-Login': 'nevladov'},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        new_situation_id = data['id']
        assert new_situation_id != situation_id
        count_after = count(new_situation_id)
        assert count_before == count_after
        data.pop('created_at')
        data.pop('updated_at')
    if expected_data is not None:
        assert data == expected_data
