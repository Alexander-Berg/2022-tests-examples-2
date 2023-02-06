import pytest


@pytest.mark.parametrize(
    'situation_id,expected_status,expected_data',
    [
        (
            1,
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
            4,
            409,
            {
                'code': 'SITUATION_IS_SYSTEM',
                'message': (
                    'Situation with id \'4\' is not editable cause it is '
                    'system'
                ),
            },
        ),
        (3, 200, None),
        (
            10,
            404,
            {
                'code': 'SITUATION_IS_NOT_FOUND',
                'message': 'Situation with id \'10\' is not found',
            },
        ),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'situation_id\' '
                    'in query: None'
                ),
            },
        ),
    ],
)
async def test_situation_delete(
        taxi_eats_compensations_matrix,
        mockserver,
        situation_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.delete(
        '/eats-compensations-matrix/v1/admin/compensation/situation/',
        params={'situation_id': situation_id},
    )
    assert response.status == expected_status
    if expected_data is not None:
        data = response.json()
        assert data == expected_data
