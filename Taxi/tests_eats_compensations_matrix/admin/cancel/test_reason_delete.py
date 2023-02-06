import pytest


@pytest.mark.parametrize(
    'reason_id,expected_status,expected_data',
    [
        (
            3,
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'2\' is not editable cause it is '
                    'already approved'
                ),
            },
        ),
        (1, 200, None),
        (
            4,
            404,
            {
                'code': 'REASON_IS_NOT_FOUND',
                'message': 'Reason with id \'4\' is not found',
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
async def test_reason_delete(
        taxi_eats_compensations_matrix,
        reason_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.delete(
        '/eats-compensations-matrix/v1/admin/cancel/reason/',
        params={'reason_id': reason_id},
    )
    assert response.status == expected_status
    if expected_data is not None:
        data = response.json()
        assert data == expected_data
