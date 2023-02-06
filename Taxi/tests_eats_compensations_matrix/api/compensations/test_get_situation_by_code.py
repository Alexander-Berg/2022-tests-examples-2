import pytest


@pytest.mark.parametrize(
    'request_json, code, expected',
    [
        (
            {
                'order_type': 'native',
                'order_delivery_type': 'our_delivery',
                'situation_code': 'small_delay',
                'device_id': '1.0.0',
                'platform_type': 'android_app',
                'app_version': '7.0.0',
                'user_agent': 'test_agent',
                'personal_phone_id': '',
            },
            200,
            {
                'situation': {
                    'code': 'small_delay',
                    'id': 1,
                    'is_need_confirmation': False,
                    'is_system': False,
                    'priority': 100,
                    'responsible': 'company',
                    'title': '<= 15 мин',
                    'violation_level': 'low',
                    'group': {
                        'description': 'Долгое ожидание доставки',
                        'id': 1,
                        'priority': 100,
                        'title': 'Долгое ожидание доставки',
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
                    'is_available_before_final_status': False,
                },
                'situation_group_title': 'Долгое ожидание доставки',
                'matrix_id': 1,
                'matrix_code': 'v.test.2',
            },
        ),
        (
            {
                'order_type': 'native',
                'order_delivery_type': 'our_delivery',
                'situation_code': 'retail_delay',
                'device_id': '1.0.0',
                'platform_type': 'android_app',
                'app_version': '7.0.0',
                'user_agent': 'test_agent',
                'personal_phone_id': '',
            },
            200,
            {
                'situation': {
                    'code': 'retail_delay',
                    'id': 2,
                    'is_need_confirmation': False,
                    'is_system': False,
                    'priority': 100,
                    'responsible': 'company',
                    'title': '30 мин',
                    'violation_level': 'low',
                    'group': {
                        'description': 'Долгое ожидание доставки',
                        'id': 1,
                        'priority': 100,
                        'title': 'Долгое ожидание доставки',
                    },
                    'extra_parameters': [],
                    'is_available_before_final_status': True,
                },
                'situation_group_title': 'Долгое ожидание доставки',
                'matrix_id': 1,
                'matrix_code': 'v.test.2',
            },
        ),
        (
            {
                'order_type': 'native',
                'order_delivery_type': 'our_delivery',
                'situation_code': 'unknown_code',
                'device_id': '1.0.0',
                'platform_type': 'android_app',
                'app_version': '7.0.0',
                'user_agent': 'test_agent',
                'personal_phone_id': '',
            },
            400,
            {'code': '404', 'message': 'Situation not found'},
        ),
        (
            {
                'order_type': 'native',
                'order_delivery_type': 'our_delivery',
                'situation_code': 'small_delay',
                'device_id': '1.0.0',
                'platform_type': '',
                'app_version': '7.0.0',
                'user_agent': 'test_agent',
                'personal_phone_id': 'phone_id_0_for_unapproved_matrix',
            },
            200,
            {
                'situation': {
                    'code': 'small_delay',
                    'id': 1,
                    'is_need_confirmation': False,
                    'is_system': False,
                    'priority': 100,
                    'responsible': 'company',
                    'title': '<= 15 мин',
                    'violation_level': 'low',
                    'group': {
                        'description': 'Долгое ожидание доставки',
                        'id': 1,
                        'priority': 100,
                        'title': 'Долгое ожидание доставки',
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
                    'is_available_before_final_status': False,
                },
                'situation_group_title': 'Долгое ожидание доставки',
                'matrix_id': 1,
                'matrix_code': 'v.test.2',
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
async def test_get_situation_by_code(
        taxi_eats_compensations_matrix,
        mockserver,
        request_json,
        code,
        expected,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/api/compensation/get_situation_by_code',
        json=request_json,
    )

    assert response.status_code == code
    assert response.json() == expected
