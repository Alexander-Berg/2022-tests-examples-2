async def test_situation_list_get(taxi_eats_compensations_matrix, mockserver):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/situation/list/',
        params={'matrix_id': 1},
    )
    assert response.json() == {
        'situations': [
            {
                'id': 1,
                'matrix_id': 1,
                'code': 'small_delay',
                'title': '<= 15 мин',
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'group_id': 1,
                'is_system': False,
            },
            {
                'id': 2,
                'matrix_id': 1,
                'code': 'medium_delay',
                'title': 'Более 15 мин',
                'order_type': ['native', 'lavka'],
                'order_delivery_type': ['marketplace', 'our_delivery'],
                'group_id': 2,
                'is_system': False,
            },
        ],
        'groups': [
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
        ],
    }


async def test_situation_list_get_error(
        taxi_eats_compensations_matrix, mockserver,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/situation/list/',
        params={'matrix_id': None},
    )
    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': 'invalid int32_t value of \'matrix_id\' in query: None',
    }
