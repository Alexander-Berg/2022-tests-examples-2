import pytest


def make_input_data():
    return {
        'type': 'order.cancel.reaction.compensation',
        'payload': {'limit': 300, 'limit_currency': 'RUB', 'rate': 20},
    }


@pytest.mark.parametrize(
    'reaction_id,input_data,expected_status,expected_data',
    [
        (
            4,
            make_input_data(),
            409,
            {
                'code': 'MATRIX_IS_ALREADY_APPROVED',
                'message': (
                    'Matrix with id \'2\' is not editable cause it is '
                    'already approved'
                ),
            },
        ),
        (
            1,
            make_input_data(),
            200,
            {
                'id': 1,
                'type': 'order.cancel.reaction.compensation',
                'payload': {'limit': 300, 'limit_currency': 'RUB', 'rate': 20},
                'label': 'Промокод 20%',
            },
        ),
        (
            5,
            make_input_data(),
            404,
            {
                'code': 'REACTION_IS_NOT_FOUND',
                'message': 'Reaction with id \'5\' is not found',
            },
        ),
        (
            10,
            make_input_data(),
            404,
            {
                'code': 'REACTION_IS_NOT_FOUND',
                'message': 'Reaction with id \'10\' is not found',
            },
        ),
    ],
)
async def test_reaction_put(
        taxi_eats_compensations_matrix,
        reaction_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.put(
        '/eats-compensations-matrix/v1/admin/cancel/reaction/',
        params={'reaction_id': reaction_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
