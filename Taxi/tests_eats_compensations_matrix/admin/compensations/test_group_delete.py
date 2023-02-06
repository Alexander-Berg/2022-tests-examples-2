import pytest


@pytest.mark.parametrize(
    'group_id,expected_status,expected_data',
    [
        (
            1,
            409,
            {
                'code': 'RELATED_SITUATIONS_EXIST',
                'message': (
                    'Unable to delete group cause some related '
                    'situations exist'
                ),
            },
        ),
        (
            None,
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'group_id\' in query: None'
                ),
            },
        ),
        (
            100500,
            404,
            {
                'code': 'SITUATION_GROUP_IS_NOT_FOUND',
                'message': 'Situation group with id \'100500\' is not found',
            },
        ),
        (3, 200, None),
    ],
)
async def test_group_delete(
        taxi_eats_compensations_matrix,
        mockserver,
        group_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.delete(
        '/eats-compensations-matrix/v1/admin/compensation/group/',
        params={'group_id': group_id},
    )
    assert response.status == expected_status
    if expected_data is not None:
        data = response.json()
        assert data == expected_data
