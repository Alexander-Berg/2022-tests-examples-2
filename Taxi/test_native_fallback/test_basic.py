import json

import pytest

SURGE_MAP_VALUES = [{'x': 0, 'y': 0, 'surge': 2.0, 'weight': 1.0}]


@pytest.mark.config(ALL_CATEGORIES=['econom', 'business'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='config_disabled',
    consumers=['surge-calculator/user'],
    clauses=[],
    default_value={'mode': 'disabled'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='config_auto_fail',
    consumers=['surge-calculator/user'],
    clauses=[],
    default_value={'mode': 'auto_fail'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='config_enabled',
    consumers=['surge-calculator/user'],
    clauses=[],
    default_value={'mode': 'enabled'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='config_bad',
    consumers=['surge-calculator/user'],
    clauses=[],
    default_value={'bad': 'config'},
)
@pytest.mark.parametrize(
    'pipeline_fail_type,mode_map',
    [
        (None, {}),
        # external error will always lead to error
        ('external', {'disabled': {'code': 500}, 'auto_fail': {'code': 500}}),
        (
            'local',
            {
                'disabled': {'code': 500},
                'auto_fail': {'expected_fallback_type': 'native_algorithm'},
            },
        ),
        (
            'local_timeout',
            {
                'disabled': {'code': 500},
                'auto_fail': {'expected_fallback_type': 'native_algorithm'},
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'default_mode,config_name,expected_fallback_type',
    [
        ('disabled', 'config_disabled', None),
        ('disabled', 'config_bad', None),
        ('disabled', 'config_non_existent', None),
        ('disabled', 'config_auto_fail', None),
        ('disabled', 'config_enabled', 'native_algorithm'),
        ('auto_fail', 'config_disabled', None),
        ('auto_fail', 'config_bad', None),
        ('auto_fail', 'config_non_existent', None),
        ('auto_fail', 'config_auto_fail', None),
        ('auto_fail', 'config_enabled', 'native_algorithm'),
        ('enabled', 'config_disabled', None),
        ('enabled', 'config_bad', 'native_algorithm'),
        ('enabled', 'config_non_existent', 'native_algorithm'),
        ('enabled', 'config_auto_fail', None),
        ('enabled', 'config_enabled', 'native_algorithm'),
    ],
)
async def test_native_fallback_basic(
        taxi_surge_calculator,
        heatmap_storage,
        mockserver,
        taxi_config,
        pipeline_fail_type,
        mode_map,
        default_mode,
        config_name,
        expected_fallback_type,
):
    candidates_requests = []

    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        nonlocal candidates_requests

        actual_request = request.json

        candidates_requests.append(actual_request)

        if pipeline_fail_type == 'external':
            return mockserver.make_response('External fail', status=400)

        response = {'radius': 2785, 'generic': {}, 'reposition': {}}

        for category in actual_request.get('allowed_classes', []):
            response['generic'][category] = {
                'free': 12,
                'free_chain': 3,
                'total': 30,
                'free_chain_groups': {'short': 3, 'medium': 3, 'long': 3},
            }

        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'}, json=response,
        )

    @mockserver.json_handler('/pin-storage/v1/get_stats/radius')
    def _get_stats_radius(request):
        return {
            'stats': {
                'pins': 1,
                'pins_with_b': 0,
                'pins_with_order': 0,
                'pins_with_driver': 0,
                'prev_pins': 0,
                'values_by_category': {},
                'global_pins': 1,
                'global_pins_with_order': 0,
                'global_pins_with_driver': 0,
            },
        }

    point_a = [37.583369, 55.778821]

    heatmap_storage.build_and_set_surge_map(
        cell_size_meter=500.123,
        envelope={
            'br': [point_a[0] - 0.00001, point_a[1] - 0.00001],
            'tl': [point_a[0] + 0.1, point_a[1] + 0.1],
        },
        values=SURGE_MAP_VALUES,
    )

    taxi_config.set_values(
        {
            'SURGE_NATIVE_FALLBACK_SETTINGS': {
                'mode': {'config': config_name, 'default': default_mode},
                'surge_by_points': {
                    'enabled_config': 'surge_by_points_enabled',
                    'force_balance_experiment': 'force_balance_calculation',
                },
                'count_by_categories': {'limit': 400, 'max_distance': 2500},
                'balance_equation': {
                    'reposition_discount_default_config': (
                        'surge_reposition_discount_default'
                    ),
                    'min_pins': 1,
                    'min_total': 1,
                    'default_chain_factor': 1.0,
                    'const_min_new_free': 2,
                    'coef_nf_pins_driver': 1.0,
                    'coef_nf_pins_order': 1.0,
                },
                'bound_coeffs': {'surge_cap_config': 'surge_limits'},
                'surge_map': {
                    'max_age': {
                        'config': 'smooth_surge_max_age',
                        'value_raw_default_sec': 600,
                        'smoothing_default_sec': 900,
                    },
                },
                'forced_linear_dependency': {
                    'use_base_surge_for': 'none',
                    'linear_dep_coef': 1.0,
                },
            },
        },
    )

    mode = default_mode
    if config_name == 'config_enabled':
        mode = 'enabled'
    elif config_name == 'config_disabled':
        mode = 'disabled'
    elif config_name == 'config_auto_fail':
        mode = 'auto_fail'

    expected_code = mode_map.get(mode, {}).get('code', 200)
    expected_fallback_type = mode_map.get(mode, {}).get(
        'expected_fallback_type', expected_fallback_type,
    )

    await taxi_surge_calculator.invalidate_caches()

    request = {
        'point_a': point_a,
        'classes': ['econom', 'business'],
        # 'payment_type' is used to trigger pipeline fail
        'payment_type': pipeline_fail_type,
    }

    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == expected_code, response.text
    if expected_code == 200:
        assert response.json().get('fallback_type') == expected_fallback_type
    # check that resource cache works between pipeline and native algorithms
    # request count for given resource shouldn't exceed 1 because
    # in case of external fail we don't use native algorithm and
    # in case of local fail response will be cached and reused
    assert len(candidates_requests) == 1, json.dumps(candidates_requests)
