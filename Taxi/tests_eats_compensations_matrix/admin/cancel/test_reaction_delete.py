import pytest


@pytest.mark.parametrize(
    'reaction_id,expected_status,expected_data',
    [
        (
            4,
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'2\' is not editable cause it is '
                    'already approved'
                ),
            },
        ),
        (3, 200, None),
        (
            5,
            404,
            {
                'code': 'REACTION_IS_NOT_FOUND',
                'message': 'Reaction with id \'5\' is not found',
            },
        ),
        (
            10,
            404,
            {
                'code': 'REACTION_IS_NOT_FOUND',
                'message': 'Reaction with id \'10\' is not found',
            },
        ),
    ],
)
async def test_reason_delete(
        taxi_eats_compensations_matrix,
        reaction_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.delete(
        '/eats-compensations-matrix/v1/admin/cancel/reaction/',
        params={'reaction_id': reaction_id},
    )
    assert response.status == expected_status
    if expected_data is not None:
        data = response.json()
        assert data == expected_data
