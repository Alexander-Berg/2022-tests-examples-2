import pytest


@pytest.mark.parametrize(
    'reason_code, code, expected',
    [
        (
            'place.unable_to_call',
            200,
            {
                'matrix_code': 'v.cancel.1',
                'reason': {
                    'code': 'place.unable_to_call',
                    'group': {'code': 'place', 'id': 1, 'name': 'Ресторан'},
                    'id': 6,
                    'matrix_version_code': 'v.cancel.1',
                },
                'group': {'code': 'place', 'id': 1, 'name': 'Ресторан'},
            },
        ),
        (
            'unknown_code',
            400,
            {'code': '404', 'message': 'Reason is not found'},
        ),
        (
            'place.unable_to_call3',
            400,
            {'code': '404', 'message': 'Reason is not found'},
        ),
        (
            'place.unable_to_call4',
            200,
            {
                'matrix_code': 'v.cancel.1',
                'reason': {
                    'code': 'place.unable_to_call4',
                    'group': {'code': 'place', 'id': 1, 'name': 'Ресторан'},
                    'id': 4,
                    'matrix_version_code': 'v.cancel.1',
                },
                'group': {'code': 'place', 'id': 1, 'name': 'Ресторан'},
            },
        ),
        (
            'place.unable_to_call5',
            400,
            {'code': '404', 'message': 'Reason is not found'},
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
@pytest.mark.experiments3(filename='eats_cancel_matrix.json')
async def test_get_reason_by_code(
        taxi_eats_compensations_matrix,
        mockserver,
        reason_code,
        code,
        expected,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/api/cancel/get_reason_by_code',
        json={
            'selection_params': {
                'order_type': 'native',
                'device_id': '100',
                'application': 'ios_app',
                'app_version': '7.0.0',
                'user_agent': 'test_agent',
                'personal_phone_id': '',
                'caller': 'operator',
                'country_code': 'ru',
                'delivery_type': 'our_delivery',
                'payment_type': 'cash',
            },
            'reason_code': reason_code,
        },
    )

    assert response.status_code == code
    assert response.json() == expected
