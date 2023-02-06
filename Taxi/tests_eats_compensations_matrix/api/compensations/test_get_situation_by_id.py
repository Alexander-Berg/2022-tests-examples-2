import pytest


@pytest.mark.parametrize(
    'situation_id, code, expected',
    [
        (
            1,
            200,
            {
                'situation': {
                    'code': 'small_delay',
                    'group': {
                        'id': 1,
                        'title': 'Долгое ожидание доставки',
                        'description': 'Долгое ожидание доставки',
                        'priority': 100,
                    },
                    'id': 1,
                    'is_need_confirmation': False,
                    'is_system': False,
                    'priority': 100,
                    'responsible': 'company',
                    'title': '<= 15 мин',
                    'violation_level': 'low',
                    'extra_parameters': [
                        {
                            'code': 'superAmount',
                            'is_required': True,
                            'type': 'string',
                        },
                    ],
                    'is_available_before_final_status': False,
                },
                'situation_group_title': 'Долгое ожидание доставки',
                'matrix_id': 1,
                'matrix_code': 'v.1.0',
            },
        ),
        (
            2,
            200,
            {
                'situation': {
                    'code': 'retail_delay',
                    'group': {
                        'id': 1,
                        'title': 'Долгое ожидание доставки',
                        'description': 'Долгое ожидание доставки',
                        'priority': 100,
                    },
                    'id': 2,
                    'is_need_confirmation': False,
                    'is_system': False,
                    'priority': 100,
                    'responsible': 'company',
                    'title': '<= 15 мин',
                    'violation_level': 'low',
                    'extra_parameters': [
                        {
                            'code': 'superAmount',
                            'is_required': True,
                            'type': 'string',
                        },
                    ],
                    'is_available_before_final_status': False,
                },
                'situation_group_title': 'Долгое ожидание доставки',
                'matrix_id': 1,
                'matrix_code': 'v.1.0',
            },
        ),
        (
            3,
            200,
            {
                'situation': {
                    'code': 'retail_delay',
                    'group': {
                        'id': 1,
                        'title': 'Долгое ожидание доставки',
                        'description': 'Долгое ожидание доставки',
                        'priority': 100,
                    },
                    'id': 3,
                    'is_need_confirmation': False,
                    'is_system': False,
                    'priority': 42,
                    'responsible': 'company',
                    'title': '30 мин',
                    'violation_level': 'low',
                    'extra_parameters': [],
                    'is_available_before_final_status': True,
                },
                'situation_group_title': 'Долгое ожидание доставки',
                'matrix_id': 1,
                'matrix_code': 'v.1.0',
            },
        ),
        (4, 400, {'code': '404', 'message': 'Situation not found'}),
    ],
)
async def test_get_situation_by_id(
        taxi_eats_compensations_matrix,
        mockserver,
        situation_id,
        code,
        expected,
):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/api/compensation/get_situation_by_id',
        params={'id': situation_id},
    )

    assert response.status_code == code
    assert response.json() == expected
