async def test_reason_list_get(taxi_eats_compensations_matrix):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/cancel/reason/list/',
        params={'matrix_id': 1},
    )
    assert response.json() == {
        'reasons': [
            {
                'id': 1,
                'matrix_id': 1,
                'group_id': 1,
                'name': 'Невозможно дозвониться до ресторана',
                'code': 'place.unable_to_call',
                'priority': 105,
                'type': 'unknown',
                'order_type': ['shop', 'pharmacy', 'bk_logist'],
                'order_delivery_type': [],
                'created_at': '2020-06-23T08:00:00+00:00',
                'updated_at': '2020-06-23T08:00:00+00:00',
                'payment_type': ['cash'],
                'allowed_callers': ['operator'],
                'allowed_countries': ['ru'],
            },
            {
                'id': 2,
                'matrix_id': 1,
                'group_id': 2,
                'name': 'Отсутствует блюдо',
                'code': 'place.missing_dish',
                'priority': 101,
                'type': 'unknown',
                'order_type': ['shop', 'pharmacy', 'bk_logist'],
                'order_delivery_type': [],
                'created_at': '2020-06-23T08:00:00+00:00',
                'updated_at': '2020-06-23T08:00:00+00:00',
                'payment_type': ['card'],
                'allowed_callers': ['operator'],
                'allowed_countries': ['kz'],
            },
        ],
        'groups': [
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
        ],
    }
