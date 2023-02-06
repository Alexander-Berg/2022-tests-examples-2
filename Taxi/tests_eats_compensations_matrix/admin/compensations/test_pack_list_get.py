async def test_pack_list_get(taxi_eats_compensations_matrix, mockserver):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/pack/list/',
        params={'situation_id': 1},
    )
    assert response.json() == {
        'compensation_packs': [
            {
                'id': 1,
                'situation_id': 1,
                'available_source': ['mail', 'call', 'chat', 'system'],
                'compensations_count': 0,
                'payment_method_type': 'all',
                'antifraud_score': 'all',
                'country': 'all',
                'delivery_class': ['regular', 'ultima', 'slow', 'fast'],
                'created_at': '2020-06-16T12:00:00+00:00',
                'updated_at': '2020-06-16T12:00:00+00:00',
            },
            {
                'id': 2,
                'situation_id': 1,
                'available_source': ['call', 'chat'],
                'compensations_count': 0,
                'payment_method_type': 'card',
                'antifraud_score': 'all',
                'country': 'all',
                'delivery_class': ['slow', 'fast'],
                'created_at': '2020-06-16T12:00:00+00:00',
                'updated_at': '2020-06-16T12:00:00+00:00',
            },
        ],
        'compensation_links': [
            {'id': 1, 'type_id': 1, 'pack_id': 1},
            {'id': 2, 'type_id': 3, 'pack_id': 2},
        ],
        'compensations': [
            {
                'id': 1,
                'type': 'promocode',
                'rate': 10.0,
                'full_refund': False,
                'notification': 'order.compensation.cancel.courier.card',
            },
            {
                'id': 3,
                'type': 'promocode',
                'rate': 10.0,
                'full_refund': False,
                'notification': 'order.compensation.cancel.place.card',
            },
        ],
    }


async def test_pack_list_get_error(taxi_eats_compensations_matrix, mockserver):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/pack/list/',
        params={'situation_id': None},
    )
    assert response.status == 400
    assert response.json() == {
        'code': '400',
        'message': 'invalid int32_t value of \'situation_id\' in query: None',
    }
