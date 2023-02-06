import pytest


@pytest.mark.parametrize(
    'param_request_body, param_response_code, param_response_body',
    [
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 1000,
                    'order_cost': 100.0,
                    'reliability_level': 'good',
                    'is_fast_cancellation': False,
                    'is_place_notified': True,
                    'is_vip': True,
                },
            },
            400,
            {},
            id='unknown_reason_id',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 7,
                    'order_cost': 100.0,
                    'reliability_level': 'good',
                    'is_fast_cancellation': False,
                    'is_place_notified': True,
                    'is_vip': True,
                },
            },
            400,
            {},
            id='deleted_reason_id',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 6,
                    'order_cost': 100.0,
                    'reliability_level': 'good',
                    'is_fast_cancellation': False,
                    'is_place_notified': True,
                    'is_vip': True,
                },
            },
            200,
            {
                'reason': {
                    'id': 6,
                    'code': 'place.technical_problem6',
                    'matrix_version_code': 'v.cancel.2',
                    'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                },
                'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                'reactions': [],
            },
            id='deleted_link',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 1,
                    'order_cost': 99.99,
                    'reliability_level': 'good',
                    'is_fast_cancellation': False,
                    'is_place_notified': True,
                    'is_vip': True,
                },
            },
            200,
            {
                'reason': {
                    'id': 1,
                    'code': 'place.unable_to_call',
                    'matrix_version_code': 'v.cancel.1',
                    'group': {'id': 1, 'code': 'place', 'name': 'Ресторан'},
                },
                'group': {'id': 1, 'code': 'place', 'name': 'Ресторан'},
                'reactions': [],
            },
            id='too_low_cost',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 2,
                    'order_cost': 100.0,
                    'reliability_level': 'other',
                    'is_fast_cancellation': False,
                    'is_place_notified': True,
                    'is_vip': True,
                },
            },
            200,
            {
                'reason': {
                    'id': 2,
                    'code': 'place.technical_problem',
                    'matrix_version_code': 'v.cancel.2',
                    'group': {'id': 2, 'code': 'client', 'name': 'Клиент'},
                },
                'group': {'id': 2, 'code': 'client', 'name': 'Клиент'},
                'reactions': [],
            },
            id='too_low_reliability',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 3,
                    'order_cost': 100.0,
                    'reliability_level': 'good',
                    'is_fast_cancellation': True,
                    'is_place_notified': True,
                    'is_vip': True,
                },
            },
            200,
            {
                'reason': {
                    'id': 3,
                    'code': 'place.technical_problem3',
                    'matrix_version_code': 'v.cancel.2',
                    'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                },
                'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                'reactions': [],
            },
            id='disabled_fast_cancellation_1',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 3,
                    'order_cost': 100.0,
                    'reliability_level': 'good',
                    'is_fast_cancellation': False,
                    'is_place_notified': True,
                    'is_vip': True,
                },
            },
            200,
            {
                'reason': {
                    'id': 3,
                    'code': 'place.technical_problem3',
                    'matrix_version_code': 'v.cancel.2',
                    'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                },
                'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                'reactions': [
                    {'id': 3, 'type': 'promocode_return', 'payload': {}},
                ],
            },
            id='disabled_fast_cancellation_2',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 4,
                    'order_cost': 100.0,
                    'reliability_level': 'good',
                    'is_fast_cancellation': False,
                    'is_place_notified': False,
                    'is_vip': True,
                },
            },
            200,
            {
                'reason': {
                    'id': 4,
                    'code': 'place.technical_problem4',
                    'matrix_version_code': 'v.cancel.2',
                    'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                },
                'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                'reactions': [],
            },
            id='disabled_before_place_notified_1',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 4,
                    'order_cost': 100.0,
                    'reliability_level': 'good',
                    'is_fast_cancellation': False,
                    'is_place_notified': True,
                    'is_vip': True,
                },
            },
            200,
            {
                'reason': {
                    'id': 4,
                    'code': 'place.technical_problem4',
                    'matrix_version_code': 'v.cancel.2',
                    'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                },
                'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                'reactions': [
                    {'id': 3, 'type': 'promocode_return', 'payload': {}},
                ],
            },
            id='disabled_before_place_notified_2',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 5,
                    'order_cost': 100.0,
                    'reliability_level': 'good',
                    'is_fast_cancellation': False,
                    'is_place_notified': True,
                    'is_vip': False,
                },
            },
            200,
            {
                'reason': {
                    'id': 5,
                    'code': 'place.technical_problem5',
                    'matrix_version_code': 'v.cancel.2',
                    'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                },
                'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                'reactions': [],
            },
            id='only_vip_1',
        ),
        pytest.param(
            {
                'selection_params': {
                    'reason_id': 5,
                    'order_cost': 100.0,
                    'reliability_level': 'good',
                    'is_fast_cancellation': False,
                    'is_place_notified': True,
                    'is_vip': True,
                },
            },
            200,
            {
                'reason': {
                    'id': 5,
                    'code': 'place.technical_problem5',
                    'matrix_version_code': 'v.cancel.2',
                    'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                },
                'group': {'id': 5, 'code': 'test', 'name': 'Тест'},
                'reactions': [
                    {'id': 3, 'type': 'promocode_return', 'payload': {}},
                ],
            },
            id='only_vip_2',
        ),
    ],
)
async def test_find_reactions(
        taxi_eats_compensations_matrix,
        param_request_body,
        param_response_code,
        param_response_body,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/api/cancel/find-reactions',
        json=param_request_body,
    )
    print(response.json())
    assert response.status_code == param_response_code

    if param_response_code == 200:
        assert response.json() == param_response_body
