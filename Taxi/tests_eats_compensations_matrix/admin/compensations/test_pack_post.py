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
    'situation_id,input_data,expected_status,expected_data',
    [
        (
            3,
            make_input_data(),
            200,
            {
                'id': 6,
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
            None,
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'situation_id\' in query: None'
                ),
            },
        ),
        (
            None,
            make_input_data(),
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'situation_id\' in query: None'
                ),
            },
        ),
        (
            3,
            {},
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 1, path \'\': '
                    'missing required field \'available_source\''
                ),
            },
        ),
        (
            3,
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
            3,
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
            3,
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
        (
            3,
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
            1,
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
                'code': 'SITUATION_IS_NOT_FOUND',
                'message': 'Situation with id \'10\' is not found',
            },
        ),
    ],
)
async def test_pack_post(
        taxi_eats_compensations_matrix,
        mockserver,
        situation_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.post(
        'eats-compensations-matrix/v1/admin/compensation/pack/',
        json=input_data,
        params={'situation_id': situation_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
