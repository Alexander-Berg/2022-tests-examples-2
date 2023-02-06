import pytest


def make_input_data():
    return {
        'title': 'Долгое ожидание доставки',
        'description': 'Долгое ожидание доставки',
        'priority': 101,
    }


@pytest.mark.parametrize(
    'group_id,input_data,expected_status,expected_data',
    [
        (
            1,
            make_input_data(),
            200,
            {
                'id': 1,
                'title': 'Долгое ожидание доставки',
                'description': 'Долгое ожидание доставки',
                'priority': 101,
            },
        ),
        (
            None,
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
            None,
            make_input_data(),
            400,
            {
                'code': '400',
                'message': (
                    'invalid int32_t value of \'group_id\' in query: None'
                ),
            },
        ),
        (
            1,
            None,
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
            1,
            {'description': 'Долгое ожидание доставки', 'priority': 101},
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
            1,
            {'title': 'Долгое ожидание доставки', 'priority': 101},
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
            1,
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
        (
            4,
            make_input_data(),
            404,
            {
                'code': 'SITUATION_GROUP_IS_NOT_FOUND',
                'message': 'Situation group with id \'4\' is not found',
            },
        ),
    ],
)
async def test_group_put(
        taxi_eats_compensations_matrix,
        mockserver,
        group_id,
        input_data,
        expected_status,
        expected_data,
):
    response = await taxi_eats_compensations_matrix.put(
        '/eats-compensations-matrix/v1/admin/compensation/group/',
        params={'group_id': group_id},
        json=input_data,
    )
    assert response.status == expected_status
    data = response.json()
    if expected_status == 200:
        data.pop('created_at')
        data.pop('updated_at')
    assert data == expected_data
