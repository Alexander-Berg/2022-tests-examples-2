import pytest


def make_input_data():
    return {
        'minimal_cost': 200,
        'minimal_eater_reliability': 'good',
        'is_allowed_before_place_confirmed': True,
        'is_allowed_for_fast_cancellation': True,
        'is_for_vip_only': True,
    }


@pytest.mark.parametrize(
    'reason_id,reaction_id,input_data,expected_status,expected_data',
    [
        (
            1,
            2,
            make_input_data(),
            200,
            {
                'id': 9,
                'reason_id': 1,
                'reaction_id': 2,
                'minimal_cost': 200,
                'minimal_eater_reliability': 'good',
                'is_allowed_before_place_confirmed': True,
                'is_allowed_for_fast_cancellation': True,
                'is_for_vip_only': True,
            },
        ),
        (
            3,
            2,
            make_input_data(),
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
            10,
            1,
            make_input_data(),
            404,
            {
                'code': 'REASON_IS_NOT_FOUND',
                'message': 'Reason with id \'10\' is not found',
            },
        ),
    ],
)
async def test_reason_reaction_post(
        taxi_eats_compensations_matrix,
        mockserver,
        reason_id,
        reaction_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/admin/cancel/reason-reaction/',
        params={'reason_id': reason_id, 'reaction_id': reaction_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    assert data == expected_data
