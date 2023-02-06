import pytest


@pytest.mark.parametrize(
    'input_data,expected_status,expected_data',
    [
        (
            {
                'title': 'Долгое ожидание доставки',
                'description': 'Долгое ожидание доставки',
                'priority': 100,
            },
            200,
            {
                'id': 4,
                'title': 'Долгое ожидание доставки',
                'description': 'Долгое ожидание доставки',
                'priority': 100,
            },
        ),
        (
            {},
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 1, path \'\': '
                    'missing required field \'title\''
                ),
            },
        ),
        (
            {'description': 'Долгое ожидание доставки', 'priority': 100},
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 169, path \'\': '
                    'missing required field \'title\''
                ),
            },
        ),
        (
            {'title': 'Долгое ожидание доставки', 'priority': 100},
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 163, path \'\': '
                    'missing required field \'description\''
                ),
            },
        ),
        (
            {
                'title': 'Долгое ожидание доставки',
                'description': 'Долгое ожидание доставки',
            },
            400,
            {
                'code': '400',
                'message': (
                    'Parse error at pos 299, path \'\': '
                    'missing required field \'priority\''
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
        '/eats-compensations-matrix/v1/admin/compensation/group/',
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
