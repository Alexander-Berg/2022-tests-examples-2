import pytest


@pytest.mark.parametrize(
    'pack_id,type_id,expected_status,expected_data',
    [
        (4, 1, 200, None),
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
            None,
            1,
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
            4,
            2,
            409,
            {
                'code': 'PACK_TO_TYPE_LINK_IS_ALREADY_EXIST',
                'message': (
                    'Link from pack with id \'4\' to type with id '
                    '\'2\' is already exist'
                ),
            },
        ),
        (
            10,
            2,
            404,
            {
                'code': 'COMPENSATION_PACK_OR_TYPE_IS_NOT_FOUND',
                'message': 'Compensation pack or type is not found',
            },
        ),
        (
            4,
            10,
            404,
            {
                'code': 'COMPENSATION_PACK_OR_TYPE_IS_NOT_FOUND',
                'message': 'Compensation pack or type is not found',
            },
        ),
    ],
)
async def test_pack_link(
        taxi_eats_compensations_matrix,
        mockserver,
        pack_id,
        type_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.put(
        'eats-compensations-matrix/v1/admin/compensation/pack/link/',
        json={'pack_id': pack_id, 'type_id': type_id},
    )
    assert response.status == expected_status
    if expected_data is not None:
        data = response.json()
        assert data == expected_data
