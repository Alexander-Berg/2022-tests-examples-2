async def test_group_list_get(taxi_eats_compensations_matrix, mockserver):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/group/list/',
    )
    assert response.json() == {
        'situation_groups': [
            {
                'id': 1,
                'title': 'Долгое ожидание доставки',
                'description': 'Долгое ожидание доставки',
                'priority': 100,
                'created_at': '2020-06-16T07:00:00+00:00',
                'updated_at': '2020-06-16T17:00:00+00:00',
            },
            {
                'id': 2,
                'title': 'Проблема с приготовлением еды',
                'description': 'Проблема с приготовлением еды',
                'priority': 99,
                'created_at': '2020-06-16T07:00:00+00:00',
                'updated_at': '2020-06-16T17:00:00+00:00',
            },
            {
                'id': 3,
                'title': 'Проблема с приготовлением еды',
                'description': 'Проблема с приготовлением еды',
                'priority': 98,
                'created_at': '2020-06-16T07:00:00+00:00',
                'updated_at': '2020-06-16T17:00:00+00:00',
            },
        ],
    }
