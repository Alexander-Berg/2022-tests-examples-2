import pytest


@pytest.mark.parametrize(
    'expected_status,expected_data',
    [
        (
            200,
            {
                'reactions': [
                    {
                        'id': 1,
                        'type': 'order.cancel.reaction.compensation',
                        'payload': {
                            'limit': 100,
                            'limit_currency': 'RUB',
                            'rate': 15,
                        },
                        'created_at': '2020-06-23T08:00:00+00:00',
                        'updated_at': '2020-06-23T08:00:00+00:00',
                        'label': 'Промокод 15%',
                    },
                    {
                        'id': 2,
                        'type': 'order.cancel.reaction.compensation',
                        'payload': {
                            'limit': 200,
                            'limit_currency': 'BYN',
                            'rate': 25,
                        },
                        'created_at': '2020-06-23T08:00:00+00:00',
                        'updated_at': '2020-06-23T08:00:00+00:00',
                        'label': 'Промокод 25%',
                    },
                    {
                        'id': 3,
                        'type': 'order.cancel.reaction.return_promocode',
                        'payload': {},
                        'created_at': '2020-06-23T08:00:00+00:00',
                        'updated_at': '2020-06-23T08:00:00+00:00',
                        'label': 'Возврат промокода',
                    },
                    {
                        'id': 4,
                        'type': 'order.cancel.reaction.return_promocode',
                        'payload': {},
                        'created_at': '2020-06-23T08:00:00+00:00',
                        'updated_at': '2020-06-23T08:00:00+00:00',
                        'label': 'Возврат промокода',
                    },
                ],
            },
        ),
    ],
)
async def test_reaction_list(
        taxi_eats_compensations_matrix, expected_status, expected_data,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/cancel/reaction/list/',
    )
    assert response.status_code == expected_status
    assert response.json() == expected_data
