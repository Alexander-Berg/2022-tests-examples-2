import pytest


@pytest.mark.parametrize(
    'selection_params, expected',
    [
        (
            {
                'application': 'ios_app',
                'app_version': '7.0.0',
                'personal_phone_id': '1',
                'caller': 'operator',
                'country_code': 'ru',
                'order_type': 'native',
                'delivery_type': 'our_delivery',
                'device_id': '100',
                'payment_type': 'cash',
                'user_agent': 'android-agent',
            },
            {
                'groups': [{'code': 'place', 'id': 1, 'name': 'Ресторан'}],
                'matrix_code': 'v.cancel.1',
                'matrix_id': 2,
                'reasons': [
                    {
                        'code': 'place.unable_to_call',
                        'group': {
                            'code': 'place',
                            'id': 1,
                            'name': 'Ресторан',
                        },
                        'id': 1,
                        'matrix_version_code': 'v.cancel.1',
                    },
                    {
                        'code': 'place.unable_to_call',
                        'group': {
                            'code': 'place',
                            'id': 1,
                            'name': 'Ресторан',
                        },
                        'id': 3,
                        'matrix_version_code': 'v.cancel.1',
                    },
                ],
            },
        ),
        (
            {
                'application': 'ios_app',
                'app_version': '7.0.0',
                'personal_phone_id': '1',
                'caller': 'operator',
                'country_code': 'il',
                'order_type': 'native',
                'delivery_type': 'our_delivery',
                'device_id': '100',
                'payment_type': 'cash',
                'user_agent': 'android-agent',
            },
            {
                'matrix_code': 'v.israel.1',
                'matrix_id': 4,
                'groups': [],
                'reasons': [],
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
@pytest.mark.experiments3(filename='eats_cancel_matrix.json')
async def test_reasons_on_experiment(
        taxi_eats_compensations_matrix, expected, selection_params,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/api/cancel/list',
        json={'selection_params': selection_params},
    )

    assert response.status_code == 200
    assert response.json() == expected
