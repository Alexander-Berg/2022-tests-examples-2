import pytest


def make_input_data():
    return {
        'type': 'order.cancel.reaction.notification',
        'payload': {'code': 'some_code'},
    }


@pytest.mark.parametrize(
    'input_data,expected_status,expected_data',
    [
        (
            make_input_data(),
            200,
            {
                'id': 6,
                'type': 'order.cancel.reaction.notification',
                'payload': {'code': 'some_code'},
                'label': 'Уведомление',
            },
        ),
    ],
)
async def test_reaction_post(
        taxi_eats_compensations_matrix,
        mockserver,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/admin/cancel/reaction/',
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
