import pytest


@pytest.mark.parametrize(
    'type_id,expected_status,expected_data',
    [
        (
            1,
            200,
            {
                'id': 1,
                'type': 'promocode',
                'rate': 10.0,
                'full_refund': False,
                'notification': 'order.compensation.cancel.courier.card',
            },
        ),
        (
            5,
            200,
            {
                'id': 5,
                'type': 'promocode',
                'rate': 42,
                'full_refund': True,
                'notification': 'order.compensation.refund',
            },
        ),
        (
            6,
            200,
            {
                'id': 6,
                'type': 'promocode',
                'rate': 42,
                'full_refund': True,
                'notification': 'order.compensation.tips_refund',
            },
        ),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'type_id\' in query: None'
                ),
            },
        ),
        (
            7,
            404,
            {
                'code': 'COMPENSATION_TYPE_IS_NOT_FOUND',
                'message': 'Compensation type with id \'7\' is not found',
            },
        ),
    ],
)
async def test_type_get(
        taxi_eats_compensations_matrix,
        mockserver,
        type_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/type/',
        params={'type_id': type_id},
    )
    assert response.status == expected_status
    data = response.json()
    assert data == expected_data
