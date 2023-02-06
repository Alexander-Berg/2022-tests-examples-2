import pytest


@pytest.mark.parametrize(
    'reaction_id,expected_status,expected_data',
    [
        (
            1,
            200,
            {
                'id': 1,
                'type': 'order.cancel.reaction.compensation',
                'payload': {'limit': 100, 'limit_currency': 'RUB', 'rate': 15},
                'created_at': '2020-06-23T08:00:00+00:00',
                'updated_at': '2020-06-23T08:00:00+00:00',
                'label': 'Промокод 15%',
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
async def test_reaction_get(
        taxi_eats_compensations_matrix,
        reaction_id,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/cancel/reaction/',
        params={'reaction_id': reaction_id},
    )
    assert response.status == expected_status
    data = response.json()
    assert data == expected_data
