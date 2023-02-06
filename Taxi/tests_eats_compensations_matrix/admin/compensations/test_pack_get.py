import pytest


@pytest.mark.parametrize(
    'pack_id,expected_status,expected_data',
    [
        (
            1,
            200,
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
        ),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'pack_id\' in query: None'
                ),
            },
        ),
        (
            10,
            404,
            {
                'code': 'COMPENSATION_PACK_IS_NOT_FOUND',
                'message': 'Compensation pack with id \'10\' is not found',
            },
        ),
    ],
)
async def test_pack_get(
        taxi_eats_compensations_matrix,
        mockserver,
        pack_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/pack/',
        params={'pack_id': pack_id},
    )
    assert response.status == expected_status
    data = response.json()
    assert data == expected_data
