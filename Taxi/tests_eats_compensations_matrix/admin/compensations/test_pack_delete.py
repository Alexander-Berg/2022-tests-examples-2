import pytest


@pytest.mark.parametrize(
    'pack_id,expected_status,expected_data',
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
        (4, 200, None),
        (5, 200, None),
        (
            10,
            404,
            {
                'code': 'COMPENSATION_PACK_IS_NOT_FOUND',
                'message': 'Compensation pack with id \'10\' is not found',
            },
        ),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'pack_id\' in query: None'
                ),
            },
        ),
    ],
)
async def test_pack_delete(
        taxi_eats_compensations_matrix,
        mockserver,
        pack_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.delete(
        'eats-compensations-matrix/v1/admin/compensation/pack/',
        params={'pack_id': pack_id},
    )
    assert response.status == expected_status
    if expected_data is not None:
        data = response.json()
        assert data == expected_data
