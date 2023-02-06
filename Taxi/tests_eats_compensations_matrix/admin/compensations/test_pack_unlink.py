import pytest


@pytest.mark.parametrize(
    'pack_id,type_id,expected_status,expected_data',
    [
        (4, 2, 200, None),
        (
            None,
            None,
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 16, path \'pack_id\': '
                    'integer was expected, but null found, '
                    'the latest token was : null'
                ),
            },
        ),
        (
            4,
            None,
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 30, path \'type_id\': '
                    'integer was expected, but null found, '
                    'the latest token was : null'
                ),
            },
        ),
        (
            None,
            2,
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 16, path \'pack_id\': '
                    'integer was expected, but null found, '
                    'the latest token was : null'
                ),
            },
        ),
        (
            1,
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
            5,
            10,
            404,
            {
                'code': 'PACK_TO_TYPE_LINK_IS_NOT_FOUND',
                'message': (
                    'Link from pack with id \'5\' to type with id '
                    '\'10\' is not found'
                ),
            },
        ),
    ],
)
async def test_pack_unlink(
        taxi_eats_compensations_matrix,
        mockserver,
        pack_id,
        type_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.post(
        'eats-compensations-matrix/v1/admin/compensation/pack/unlink/',
        json={'pack_id': pack_id, 'type_id': type_id},
    )
    assert response.status == expected_status
    if expected_data is not None:
        data = response.json()
        assert data == expected_data
