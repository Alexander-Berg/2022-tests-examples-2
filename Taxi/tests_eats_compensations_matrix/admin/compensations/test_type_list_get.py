async def test_type_list_get(taxi_eats_compensations_matrix, mockserver):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/type/list/',
    )
    assert response.json() == {
        'compensation_types': [
            {
                'id': 1,
                'type': 'promocode',
                'rate': 10.0,
                'full_refund': False,
                'notification': 'order.compensation.cancel.courier.card',
            },
            {
                'id': 2,
                'type': 'promocode',
                'rate': 10.0,
                'full_refund': False,
                'notification': 'order.compensation.cancel.courier.cash',
            },
            {
                'id': 3,
                'type': 'promocode',
                'rate': 10.0,
                'full_refund': False,
                'notification': 'order.compensation.cancel.place.card',
            },
            {
                'id': 4,
                'type': 'promocode',
                'rate': 10.0,
                'full_refund': False,
                'notification': 'order.compensation.cancel.place.card',
            },
            {
                'id': 5,
                'type': 'promocode',
                'rate': 42,
                'full_refund': True,
                'notification': 'order.compensation.refund',
            },
            {
                'id': 6,
                'type': 'promocode',
                'rate': 42,
                'full_refund': True,
                'notification': 'order.compensation.tips_refund',
            },
        ],
    }
