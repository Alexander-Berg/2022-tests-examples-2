import pytest


@pytest.mark.parametrize(
    'reason_id,expected_status,expected_data',
    [
        (
            1,
            200,
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
                'allowed_callers': ['operator'],
                'allowed_countries': ['ru'],
                'payment_type': ['cash'],
            },
        ),
        (
            10,
            404,
            {
                'code': 'REASON_IS_NOT_FOUND',
                'message': 'Reason with id \'10\' is not found',
            },
        ),
    ],
)
async def test_reason_get(
        taxi_eats_compensations_matrix,
        reason_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/cancel/reason/',
        params={'reason_id': reason_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
