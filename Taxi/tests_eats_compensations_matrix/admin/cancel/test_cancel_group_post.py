import pytest


@pytest.mark.parametrize(
    'input_data,expected_status,expected_data',
    [
        (
            {'code': 'eater', 'name': 'Ресторан 1'},
            200,
            {'id': 4, 'code': 'eater', 'name': 'Ресторан 1'},
        ),
        (
            {'code': 'place', 'name': 'Ресторан 1'},
            409,
            {
                'code': 'GROUP_CODE_EXISTS',
                'message': (
                    'Unable to insert group cause group with code '
                    '\'place\' already exists'
                ),
            },
        ),
    ],
)
async def test_group_post(
        taxi_eats_compensations_matrix,
        mockserver,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/admin/cancel/group/', json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
