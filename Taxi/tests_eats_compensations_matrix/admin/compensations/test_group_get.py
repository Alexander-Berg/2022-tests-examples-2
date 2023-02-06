import pytest


@pytest.mark.parametrize(
    'group_id,expected_status,expected_data',
    [
        (
            1,
            200,
            {
                'id': 1,
                'title': 'Долгое ожидание доставки',
                'description': 'Долгое ожидание доставки',
                'priority': 100,
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
            10,
            404,
            {
                'code': 'SITUATION_GROUP_IS_NOT_FOUND',
                'message': 'Situation group with id \'10\' is not found',
            },
        ),
    ],
)
async def test_group_get(
        taxi_eats_compensations_matrix,
        mockserver,
        group_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/group/',
        params={'group_id': group_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
