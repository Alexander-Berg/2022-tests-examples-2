import pytest


@pytest.mark.parametrize(
    'reason_reaction_id,expected_status,expected_data',
    [
        (1, 200, {}),
        (
            5,
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
            404,
            {
                'code': 'REASON_REACTION_IS_NOT_FOUND',
                'message': 'Reason reaction with id \'10\' is not found',
            },
        ),
        (
            6,
            404,
            {
                'code': 'REASON_REACTION_IS_NOT_FOUND',
                'message': 'Reason reaction with id \'6\' is not found',
            },
        ),
    ],
)
async def test_reason_reaction_delete(
        taxi_eats_compensations_matrix,
        mockserver,
        reason_reaction_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.delete(
        '/eats-compensations-matrix/v1/admin/cancel/reason-reaction/',
        params={'reason_reaction_id': reason_reaction_id},
    )
    assert response.status == expected_status
    if response.status != 200:
        data = response.json()
        assert data == expected_data
