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
    'reason_reaction_id,input_data,expected_status,expected_data',
    [
        (
            1,
            make_input_data(),
            200,
            {
                'id': 1,
                'reason_id': 1,
                'reaction_id': 1,
                'minimal_cost': 200,
                'minimal_eater_reliability': 'good',
                'is_allowed_before_place_confirmed': True,
                'is_allowed_for_fast_cancellation': True,
                'is_for_vip_only': True,
            },
        ),
        (
            5,
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
            make_input_data(),
            404,
            {
                'code': 'REASON_REACTION_IS_NOT_FOUND',
                'message': 'Reason reaction with id \'10\' is not found',
            },
        ),
        (
            6,
            make_input_data(),
            404,
            {
                'code': 'REASON_REACTION_IS_NOT_FOUND',
                'message': 'Reason reaction with id \'6\' is not found',
            },
        ),
    ],
)
async def test_reason_reaction_put(
        taxi_eats_compensations_matrix,
        mockserver,
        reason_reaction_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.put(
        '/eats-compensations-matrix/v1/admin/cancel/reason-reaction/',
        params={'reason_reaction_id': reason_reaction_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    assert data == expected_data
