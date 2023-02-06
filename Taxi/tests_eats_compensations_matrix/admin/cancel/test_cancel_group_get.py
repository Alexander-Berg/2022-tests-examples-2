import pytest


@pytest.mark.parametrize(
    'group_id,expected_status,expected_data',
    [
        (1, 200, {'code': 'place', 'id': 1, 'name': 'Ресторан'}),
        (
            4,
            404,
            {
                'code': 'REASON_GROUP_IS_NOT_FOUND',
                'message': 'Reason group with id \'4\' is not found',
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
        '/eats-compensations-matrix/v1/admin/cancel/group/',
        params={'group_id': group_id},
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
