import pytest


@pytest.mark.parametrize(
    'request_data,expected',
    [
        (
            {
                'device_id': '100',
                'order_type': 'retail',
                'order_delivery_type': 'pickup',
                'personal_phone_id': 'none',
            },
            {'situations': [], 'matrix_id': 2, 'matrix_code': 'v.test.1'},
        ),
        (
            {
                'device_id': '101',
                'order_type': 'native',
                'order_delivery_type': 'our_delivery',
                'personal_phone_id': 'none',
            },
            {'situations': [], 'matrix_id': 3, 'matrix_code': 'v.test.2'},
        ),
        (
            {
                'order_type': 'native',
                'order_delivery_type': 'our_delivery',
                'personal_phone_id': 'none',
            },
            {
                'situations': [
                    {
                        'id': 1,
                        'group': {
                            'id': 1,
                            'title': 'Долгое ожидание доставки',
                            'description': 'Долгое ожидание доставки',
                            'priority': 100,
                        },
                        'extra_parameters': [
                            {
                                'code': 'products',
                                'is_required': True,
                                'type': 'string',
                            },
                            {
                                'code': 'superAmount',
                                'is_required': True,
                                'type': 'string',
                            },
                        ],
                        'title': '<= 15 мин',
                        'code': 'small_delay',
                        'violation_level': 'low',
                        'responsible': 'company',
                        'priority': 100,
                        'is_system': False,
                        'is_need_confirmation': False,
                        'is_available_before_final_status': False,
                    },
                    {
                        'id': 2,
                        'group': {
                            'id': 1,
                            'title': 'Долгое ожидание доставки',
                            'description': 'Долгое ожидание доставки',
                            'priority': 100,
                        },
                        'extra_parameters': [
                            {
                                'code': 'superAmount',
                                'is_required': True,
                                'type': 'string',
                            },
                        ],
                        'title': '<= 15 мин',
                        'code': 'small_delay',
                        'violation_level': 'low',
                        'responsible': 'company',
                        'priority': 100,
                        'is_system': False,
                        'is_need_confirmation': False,
                        'is_available_before_final_status': False,
                    },
                    {
                        'id': 4,
                        'group': {
                            'id': 1,
                            'title': 'Долгое ожидание доставки',
                            'description': 'Долгое ожидание доставки',
                            'priority': 100,
                        },
                        'extra_parameters': [],
                        'title': '30 мин retail',
                        'code': 'retail_delay',
                        'violation_level': 'low',
                        'responsible': 'company',
                        'priority': 42,
                        'is_system': False,
                        'is_need_confirmation': False,
                        'is_available_before_final_status': True,
                    },
                ],
                'matrix_id': 1,
                'matrix_code': 'v.1.0',
            },
        ),
        (
            {
                'order_type': 'retail',
                'order_delivery_type': 'our_delivery',
                'personal_phone_id': 'none',
            },
            {
                'situations': [
                    {
                        'id': 3,
                        'group': {
                            'id': 1,
                            'title': 'Долгое ожидание доставки',
                            'description': 'Долгое ожидание доставки',
                            'priority': 100,
                        },
                        'extra_parameters': [],
                        'title': '<= 15 мин retail',
                        'code': 'small_delay',
                        'violation_level': 'low',
                        'responsible': 'company',
                        'priority': 100,
                        'is_system': False,
                        'is_need_confirmation': False,
                        'is_available_before_final_status': False,
                    },
                ],
                'matrix_id': 1,
                'matrix_code': 'v.1.0',
            },
        ),
        (
            {
                'order_type': 'retail',
                'order_delivery_type': 'our_delivery',
                'personal_phone_id': 'phone_id_1_for_unapproved_matrix',
            },
            {
                'situations': [
                    {
                        'id': 3,
                        'group': {
                            'id': 1,
                            'title': 'Долгое ожидание доставки',
                            'description': 'Долгое ожидание доставки',
                            'priority': 100,
                        },
                        'extra_parameters': [],
                        'title': '<= 15 мин retail',
                        'code': 'small_delay',
                        'violation_level': 'low',
                        'responsible': 'company',
                        'priority': 100,
                        'is_system': False,
                        'is_need_confirmation': False,
                        'is_available_before_final_status': False,
                    },
                ],
                'matrix_id': 1,
                'matrix_code': 'v.1.0',
            },
        ),
        (
            {
                'device_id': '100',
                'order_type': 'retail',
                'order_delivery_type': 'pickup',
                'personal_phone_id': 'none',
                'country_code': 'il',
            },
            {'situations': [], 'matrix_id': 6, 'matrix_code': 'v.israel.1'},
        ),
        (
            {
                'device_id': '100',
                'order_type': 'lavka',
                'order_delivery_type': 'pickup',
                'personal_phone_id': 'none',
                'country_code': 'ru',
            },
            {
                'situations': [],
                'matrix_id': 11,
                'matrix_code': 'v.lavka_test.1',
            },
        ),
        (
            {
                'device_id': '100',
                'order_type': 'lavka',
                'order_delivery_type': 'pickup',
                'personal_phone_id': 'none',
                'country_code': 'ru',
                'is_grocery_flow': True,
            },
            {
                'situations': [],
                'matrix_id': 12,
                'matrix_code': 'v.lavka_test.2',
            },
        ),
        (
            {
                'device_id': '100',
                'order_type': 'lavka',
                'order_delivery_type': 'pickup',
                'personal_phone_id': 'none',
                'country_code': 'ru',
                'is_grocery_flow': True,
                'has_ya_plus': True,
            },
            {
                'situations': [
                    {
                        'id': 5,
                        'group': {
                            'id': 21,
                            'title': 'Баллы Плюса',
                            'description': 'Компенсации баллами Плюса',
                            'priority': 1,
                        },
                        'extra_parameters': [
                            {
                                'code': 'products',
                                'is_required': True,
                                'type': 'string',
                            },
                        ],
                        'title': 'Баллы Плюса - процент от суммы',
                        'code': 'test_percent_plus',
                        'violation_level': 'low',
                        'responsible': 'company',
                        'priority': 1,
                        'is_system': False,
                        'is_need_confirmation': False,
                        'is_available_before_final_status': True,
                    },
                ],
                'matrix_id': 13,
                'matrix_code': 'v.lavka_test.2p',
            },
        ),
    ],
)
@pytest.mark.config(
    EATS_COMPENSATIONS_MATRIX_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 5000,
        'experiment_name': 'compensation_matrix_exp_test',
        'compensation_fallback_id': 1,
        'cancel_fallback_id': 1,
    },
)
@pytest.mark.experiments3(filename='eats_compensation_matrix.json')
async def test_situations_on_experiment(
        taxi_eats_compensations_matrix, mockserver, request_data, expected,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/api/compensation/list',
        json=request_data,
    )

    assert response.status_code == 200
    assert response.json() == expected
