import pytest


@pytest.mark.parametrize(
    'input_data,expected_status,expected_data',
    [
        (
            {
                'type': 'promocode',
                'rate': 10.0,
                'full_refund': False,
                'notification': 'order.compensation.promocode',
            },
            200,
            {
                'id': 7,
                'type': 'promocode',
                'rate': 10.0,
                'full_refund': False,
                'notification': 'order.compensation.promocode',
            },
        ),
        (
            {
                'type': 'superRefund',
                'full_refund': False,
                'notification': 'order.compensation.refund',
            },
            200,
            {
                'id': 7,
                'type': 'superRefund',
                'full_refund': False,
                'notification': 'order.compensation.refund',
            },
        ),
        (
            {
                'type': 'promocode',
                'rate': -5,
                'full_refund': False,
                'notification': 'order.compensation.promocode',
            },
            400,
            {
                'code': 'RATE_HAS_INCORRECT_FORMAT',
                'message': (
                    'Rate of promocode must be in range from 0 to 100 '
                    'and must be integer'
                ),
            },
        ),
        (
            {
                'type': 'promocode',
                'rate': 105,
                'full_refund': False,
                'notification': 'order.compensation.promocode',
            },
            400,
            {
                'code': 'RATE_HAS_INCORRECT_FORMAT',
                'message': (
                    'Rate of promocode must be in range from 0 to 100 '
                    'and must be integer'
                ),
            },
        ),
        (
            {
                'type': 'promocode',
                'rate': 10.5,
                'full_refund': False,
                'notification': 'order.compensation.promocode',
            },
            400,
            {
                'code': '400',
                # 'message': 'Request parser error with type mismatch',
            },
        ),
    ],
)
async def test_type_post(
        taxi_eats_compensations_matrix,
        mockserver,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/admin/compensation/type/',
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()

    # If 'rate' is not integer or round float then ignore 'message',
    # because it contains parser error text which can change.
    if 'rate' in input_data:
        if input_data['rate'] != int(input_data['rate']):
            data.pop('message')

    assert data == expected_data
