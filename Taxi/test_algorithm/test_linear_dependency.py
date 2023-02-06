# pylint: disable=W0621
import pytest

from .. import common


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'], SURGE_ENABLE_SURCHARGE=True,
)
@pytest.mark.parametrize(
    'use_base_class_table,enable_native_fallback,apply_bounds,expected_result',
    [
        (
            False,
            False,
            False,
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 2,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'uberx',
                        'reason': 'linear_dependency',
                        'surcharge': 349,
                        'surcharge_alpha': 0.9,
                        'surcharge_beta': 0.1,
                        'value': 20.8,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Beloruss',
            },
        ),
        (
            False,
            False,
            True,
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 2,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'uberx',
                        'reason': 'linear_dependency',
                        'surcharge': 349,
                        'surcharge_alpha': 0.9,
                        'surcharge_beta': 0.1,
                        'value': 20.8,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Beloruss',
            },
        ),
        (
            True,
            False,
            False,
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 2,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'uberx',
                        'reason': 'linear_dependency',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 2,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Beloruss',
            },
        ),
        (
            True,
            False,
            True,
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 2,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'uberx',
                        'reason': 'linear_dependency',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 1.5,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Beloruss',
            },
        ),
        # native fallback bounds linear dependency and smoothes differently,
        # so results differ
        (
            False,
            True,
            False,
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 2,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'uberx',
                        'reason': 'linear_dependency',
                        'surcharge': 159,
                        'surcharge_alpha': 0.9,
                        'surcharge_beta': 0.1,
                        'value': 1.8,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Beloruss',
            },
        ),
        (
            False,
            True,
            True,
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 2,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'uberx',
                        'reason': 'linear_dependency',
                        'surcharge': 159,
                        'surcharge_alpha': 0.9,
                        'surcharge_beta': 0.1,
                        'value': 1.8,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Beloruss',
            },
        ),
        (
            True,
            True,
            False,
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 2,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'uberx',
                        'reason': 'linear_dependency',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 1.5,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Beloruss',
            },
        ),
        (
            True,
            True,
            True,
            {
                'classes': [
                    {
                        'antisurge': False,
                        'name': 'econom',
                        'reason': 'rain',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 2,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                    {
                        'antisurge': False,
                        'name': 'uberx',
                        'reason': 'linear_dependency',
                        'surcharge': 0,
                        'surcharge_alpha': 1,
                        'surcharge_beta': 0,
                        'value': 1.5,
                        'value_raw': 23,
                        'value_smooth': 1,
                        'value_smooth_is_default': True,
                    },
                ],
                'experiments': [],
                'method': 1,
                'zone_id': 'MSK-Beloruss',
            },
        ),
    ],
)
async def test(
        taxi_surge_calculator,
        admin_surger,
        taxi_config,
        enable_native_fallback,
        use_base_class_table,
        apply_bounds,
        expected_result,
):
    if enable_native_fallback:
        for class_info in expected_result['classes']:
            # fallback uses value_raw as default smooth surge by default
            if class_info['value_smooth_is_default']:
                class_info['value_smooth'] = class_info['value_raw']

    expected_result = common.convert_response(
        expected_result, {'experiment_id': 'b66bf587447b401a9e365c1cdffa4ba5'},
    )

    if enable_native_fallback:
        expected_result['calculation_type'] = 'default'
        expected_result['fallback_type'] = 'native_algorithm'

    for zone in admin_surger.zones.values():
        if zone['forced']:
            for exp in zone['forced']:
                exp['rules']['uberx']['linear_dependency_formula'][
                    'use_base_class_table'
                ] = use_base_class_table

    taxi_config.set_values(
        {
            'SURGE_NATIVE_FALLBACK_FORCE': enable_native_fallback,
            'SURGE_APPLY_BOUNDS_TO_LINEAR_DEPENDENCY_WITH_BASE_TABLE': (
                apply_bounds
            ),
        },
    )

    await taxi_surge_calculator.invalidate_caches()

    req = {
        'tariffs': ['econom', 'uberx'],
        'point_a': [37.58829620633788, 55.77425398624534],
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=req)

    assert response.status == 200, response.text
    actual_result = response.json()
    common.sort_data(actual_result)
    assert len(actual_result.pop('calculation_id', '')) == 32
    assert actual_result == expected_result
