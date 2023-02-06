import pytest


def make_input_data():
    return {
        'available_source': ['mail', 'call', 'chat', 'system'],
        'compensations_count': 0,
        'payment_method_type': 'all',
        'antifraud_score': 'all',
        'country': 'all',
        'delivery_class': ['regular', 'ultima'],
    }


@pytest.mark.parametrize(
    'pack_id,input_data,expected_status,expected_data',
    [
        (
            4,
            make_input_data(),
            200,
            {
                'id': 4,
                'situation_id': 3,
                'available_source': ['mail', 'call', 'chat', 'system'],
                'compensations_count': 0,
                'payment_method_type': 'all',
                'antifraud_score': 'all',
                'country': 'all',
                'delivery_class': ['regular', 'ultima'],
            },
        ),
        (
            3,
            make_input_data(),
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'1\' is not editable cause it is '
                    'already approved'
                ),
            },
        ),
        (
            10,
            make_input_data(),
            404,
            {
                'code': 'COMPENSATION_PACK_IS_NOT_FOUND',
                'message': 'Compensation pack with id \'10\' is not found',
            },
        ),
        (
            4,
            {
                'payment_method_type': 'all',
                'antifraud_score': 'all',
                'country': 'all',
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 73, path \'\': '
                    'missing required field \'available_source\''
                ),
            },
        ),
        (
            4,
            {
                'available_source': ['mail', 'call', 'chat', 'system'],
                'antifraud_score': 'all',
                'country': 'all',
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 99, path \'\': '
                    'missing required field \'payment_method_type\''
                ),
            },
        ),
        (
            4,
            {
                'available_source': ['mail', 'call', 'chat', 'system'],
                'payment_method_type': 'all',
                'country': 'all',
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 103, path \'\': '
                    'missing required field \'antifraud_score\''
                ),
            },
        ),
        (
            4,
            {
                'available_source': ['mail', 'call', 'chat', 'system'],
                'payment_method_type': 'all',
                'antifraud_score': 'all',
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 111, path \'\': '
                    'missing required field \'country\''
                ),
            },
        ),
    ],
)
async def test_pack_put(
        taxi_eats_compensations_matrix,
        mockserver,
        pack_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.put(
        'eats-compensations-matrix/v1/admin/compensation/pack/',
        json=input_data,
        params={'pack_id': pack_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
