import pytest


def make_input_data(group_id):
    return {
        'group_id': group_id,
        'name': 'Невозможно дозвониться до ресторана',
        'code': 'place.unable_to_call',
        'priority': 105,
        'type': 'unknown',
        'order_type': ['shop', 'pharmacy', 'bk_logist'],
        'order_delivery_type': ['our_delivery'],
        'payment_type': ['cash'],
        'allowed_callers': ['operator'],
        'allowed_countries': ['ru'],
    }


@pytest.mark.parametrize(
    'reason_id,input_data,expected_status,expected_data',
    [
        (
            3,
            make_input_data(1),
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'2\' is not editable cause it is '
                    'already approved'
                ),
            },
        ),
        (
            1,
            make_input_data(1),
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
                'order_delivery_type': ['our_delivery'],
                'payment_type': ['cash'],
                'allowed_callers': ['operator'],
                'allowed_countries': ['ru'],
            },
        ),
        (
            4,
            make_input_data(1),
            404,
            {
                'code': 'REASON_IS_NOT_FOUND',
                'message': 'Reason with id \'4\' is not found',
            },
        ),
        (
            10,
            make_input_data(1),
            404,
            {
                'code': 'REASON_IS_NOT_FOUND',
                'message': 'Reason with id \'10\' is not found',
            },
        ),
        (
            1,
            make_input_data(10),
            404,
            {
                'code': 'MATRIX_OR_GROUP_IS_NOT_FOUND',
                'message': 'Related matrix or group is not found',
            },
        ),
    ],
)
async def test_reason_put(
        taxi_eats_compensations_matrix,
        reason_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.put(
        '/eats-compensations-matrix/v1/admin/cancel/reason/',
        params={'reason_id': reason_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
