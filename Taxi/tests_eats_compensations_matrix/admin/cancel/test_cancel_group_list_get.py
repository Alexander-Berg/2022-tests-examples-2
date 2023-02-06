async def test_group_list_get(taxi_eats_compensations_matrix, mockserver):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/cancel/group/list/',
    )
    assert response.json() == {
        'reason_groups': [
            {
                'id': 1,
                'name': 'Ресторан',
                'code': 'place',
                'created_at': '2020-06-23T08:00:00+00:00',
                'updated_at': '2020-06-23T08:00:00+00:00',
            },
            {
                'id': 2,
                'name': 'Клиент',
                'code': 'client',
                'created_at': '2020-06-23T08:00:00+00:00',
                'updated_at': '2020-06-23T08:00:00+00:00',
            },
            {
                'id': 3,
                'name': 'Курьер',
                'code': 'courier',
                'created_at': '2020-06-23T08:00:00+00:00',
                'updated_at': '2020-06-23T08:00:00+00:00',
            },
        ],
    }
