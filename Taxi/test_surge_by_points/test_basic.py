# pylint: disable=W0621
import pytest

from .. import common

SURGE_MAP_VALUES = [{'x': 0, 'y': 0, 'surge': 2.0, 'weight': 1.0}]


# this config affects order of categories passed into pipeline
@pytest.mark.config(ALL_CATEGORIES=['business', 'comfortplus', 'econom'])
@pytest.mark.parametrize(
    'intent,enable_native_fallback,has_surge_in_map,surge_by_points_enabled,'
    'forced_balance_enabled,expected_response_override,'
    'expected_resource_requests_override',
    [
        pytest.param(
            None,  # intent
            False,  # enable_native_fallback
            False,  # has_surge_in_map
            False,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {},  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_1',
        ),
        pytest.param(
            None,  # intent
            False,  # enable_native_fallback
            True,  # has_surge_in_map
            False,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {
                'classes': [
                    {
                        # econom
                        'surge': {'value': 1.9},
                        'calculation_meta': {
                            'smooth': {
                                'point_a': {'value': 2.0, 'is_default': False},
                            },
                        },
                    },
                    {
                        # business
                    },
                    {
                        # comfortplus:
                        # affected by econom via weighted adjustment
                        'surge': {'value': 1.6},
                    },
                ],
            },  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_2',
        ),
        pytest.param(
            'price_calculation',  # intent
            False,  # enable_native_fallback
            False,  # has_surge_in_map
            False,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {},  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_3',
        ),
        pytest.param(
            'price_calculation',  # intent
            False,  # enable_native_fallback
            True,  # has_surge_in_map
            False,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {
                'classes': [
                    {
                        'surge': {'value': 1.9},
                        'calculation_meta': {
                            'smooth': {
                                'point_a': {'value': 2.0, 'is_default': False},
                            },
                        },
                    },
                    {
                        # business
                    },
                    {
                        # comfortplus:
                        # affected by econom via weighted adjustment
                        'surge': {'value': 1.6},
                    },
                ],
            },  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_4',
        ),
        pytest.param(
            'price_calculation',  # intent
            False,  # enable_native_fallback
            False,  # has_surge_in_map
            True,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {},  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_5',
        ),
        pytest.param(
            'price_calculation',  # intent
            False,  # enable_native_fallback
            True,  # has_surge_in_map
            True,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {
                'calculation_type': 'user_light',
                'classes': [
                    {
                        # econom: pins_free, map value: use map value
                        'value_raw': 2.0,
                        'surge': {'value': 2.0},
                        'calculation_meta': common.JsonOverrideOverwrite(
                            {
                                'reason': 'pins_free',
                                'smooth': {
                                    'point_a': {
                                        'value': 2.0,
                                        'is_default': False,
                                    },
                                },
                            },
                        ),
                    },
                    {
                        # business: pins_free, no map value,
                        # no weighted adjustment: linear dependency fallback
                        'value_raw': 2.0,
                        'surge': {'value': 2.0},
                        'calculation_meta': common.JsonOverrideOverwrite(
                            {
                                'reason': 'linear_dependency',
                                'smooth': {
                                    'point_a': {
                                        'value': 2.0,
                                        'is_default': False,
                                    },
                                },
                            },
                        ),
                    },
                    {
                        # comfortplus: pins_free, no map value,
                        # weighted adjustment: rely on weighted adjustment
                        'value_raw': 1.0,
                        'surge': {'value': 1.6},
                        'calculation_meta': common.JsonOverrideOverwrite(
                            {
                                'reason': 'pins_free',
                                'smooth': {
                                    'point_a': {
                                        'value': 1.0,
                                        'is_default': True,
                                    },
                                },
                            },
                        ),
                    },
                ],
            },  # expected_response_override
            common.JsonOverrideOverwrite([]),  # expected_resource_requests
            id='user_light',
        ),
        pytest.param(
            'price_calculation',  # intent
            False,  # enable_native_fallback
            False,  # has_surge_in_map
            False,  # surge_by_points_enabled
            True,  # forced_balance_enabled
            {'calculation_type': 'user_balance'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='user_balance_1',
        ),
        pytest.param(
            'price_calculation',  # intent
            False,  # enable_native_fallback
            False,  # has_surge_in_map
            True,  # surge_by_points_enabled
            True,  # forced_balance_enabled
            {'calculation_type': 'user_balance'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='user_balance_2',
        ),
        pytest.param(
            'price_calculation',  # intent
            False,  # enable_native_fallback
            True,  # has_surge_in_map
            True,  # surge_by_points_enabled
            True,  # forced_balance_enabled
            {
                'calculation_type': 'user_balance',
                'classes': [
                    {
                        'surge': {'value': 1.9},
                        'calculation_meta': {
                            'smooth': {
                                'point_a': {'value': 2.0, 'is_default': False},
                            },
                        },
                    },
                    {
                        # business
                    },
                    {
                        # comfortplus:
                        # affected by econom via weighted adjustment
                        'surge': {'value': 1.6},
                    },
                ],
            },  # expected_response_override
            [],  # expected_resource_requests_override
            id='user_balance_3',
        ),
        pytest.param(
            'surge_sampling',  # intent
            False,  # enable_native_fallback
            True,  # has_surge_in_map (irrelevant)
            True,  # surge_by_points_enabled (irrelevant)
            True,  # forced_balance_enabled (irrelevant)
            {
                'calculation_type': 'fixed_point',
                'classes': [
                    {
                        'surge': {'value': 1.9},
                        'calculation_meta': {
                            'smooth': {
                                'point_a': {'value': 2.0, 'is_default': False},
                            },
                        },
                    },
                    {
                        # business
                    },
                    {
                        # comfortplus:
                        # affected by econom via weighted adjustment
                        'surge': {'value': 1.6},
                    },
                ],
            },  # expected_response_override
            [],  # expected_resource_requests_override
            id='fixed_point_1',
        ),
        pytest.param(
            'surge_sampling',  # intent
            False,  # enable_native_fallback
            False,  # has_surge_in_map (irrelevant)
            True,  # surge_by_points_enabled (irrelevant)
            True,  # forced_balance_enabled (irrelevant)
            {'calculation_type': 'fixed_point'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='fixed_point_2',
        ),
        pytest.param(
            'surge_sampling',  # intent
            False,  # enable_native_fallback
            False,  # has_surge_in_map (irrelevant)
            False,  # surge_by_points_enabled (irrelevant)
            True,  # forced_balance_enabled (irrelevant)
            {'calculation_type': 'fixed_point'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='fixed_point_3',
        ),
        pytest.param(
            'surge_sampling',  # intent
            False,  # enable_native_fallback
            False,  # has_surge_in_map (irrelevant)
            False,  # surge_by_points_enabled (irrelevant)
            False,  # forced_balance_enabled (irrelevant)
            {'calculation_type': 'fixed_point'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='fixed_point_4',
        ),
        pytest.param(
            None,  # intent
            True,  # enable_native_fallback
            False,  # has_surge_in_map
            False,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {},  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_1_native',
        ),
        pytest.param(
            None,  # intent
            True,  # enable_native_fallback
            True,  # has_surge_in_map
            False,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {
                'fallback_type': 'native_algorithm',
                'classes': [
                    {
                        # econom
                        'surge': {'value': 2.0},
                        'value_raw': 1.8,
                        'calculation_meta': {
                            'ps': 4.466666666666667,
                            'f_derivative': common.JsonOverrideDelete(),
                            'smooth': {
                                'point_a': {'value': 2.0, 'is_default': False},
                            },
                        },
                    },
                    {
                        # business
                    },
                    {
                        # comfortplus:
                        # affected by econom via weighted adjustment
                        'surge': {'value': 1.6},
                    },
                ],
            },  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_2_native',
        ),
        pytest.param(
            'price_calculation',  # intent
            True,  # enable_native_fallback
            False,  # has_surge_in_map
            False,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {},  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_3_native',
        ),
        pytest.param(
            'price_calculation',  # intent
            True,  # enable_native_fallback
            True,  # has_surge_in_map
            False,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {
                'fallback_type': 'native_algorithm',
                'classes': [
                    {  # econom
                        'surge': {'value': 2.0},
                        'value_raw': 1.8,
                        'calculation_meta': {
                            'ps': 4.466666666666667,
                            'f_derivative': common.JsonOverrideDelete(),
                            'smooth': {
                                'point_a': {'value': 2.0, 'is_default': False},
                            },
                        },
                    },
                    {
                        # business
                    },
                    {
                        # comfortplus:
                        # affected by econom via weighted adjustment
                        'surge': {'value': 1.6},
                    },
                ],
            },  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_4_native',
        ),
        pytest.param(
            'price_calculation',  # intent
            True,  # enable_native_fallback
            False,  # has_surge_in_map
            True,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {},  # expected_response_override
            [],  # expected_resource_requests_override
            id='default_5_native',
        ),
        pytest.param(
            'price_calculation',  # intent
            True,  # enable_native_fallback
            True,  # has_surge_in_map
            True,  # surge_by_points_enabled
            False,  # forced_balance_enabled
            {
                'calculation_type': 'user_light',
                'fallback_type': 'native_algorithm',
                'classes': [
                    {
                        # econom: pins_free, map value: use map value
                        'value_raw': 2.0,
                        'surge': {'value': 2.0},
                        'calculation_meta': common.JsonOverrideOverwrite(
                            {
                                'reason': 'pins_free',
                                'smooth': {
                                    'point_a': {
                                        'value': 2.0,
                                        'is_default': False,
                                    },
                                },
                            },
                        ),
                    },
                    {
                        # business: pins_free, no map value,
                        # no weighted adjustment: linear dependency fallback
                        'value_raw': 2.0,
                        'surge': {'value': 2.0},
                        'calculation_meta': common.JsonOverrideOverwrite(
                            {
                                'degradation_level': 'linear_dependency',
                                'reason': 'linear_dependency',
                                'smooth': {
                                    'point_a': {
                                        'value': 2.0,
                                        'is_default': False,
                                    },
                                },
                            },
                        ),
                    },
                    {
                        # comfortplus: pins_free, no map value,
                        # weighted adjustment: rely on weighted adjustment
                        'value_raw': 1.0,
                        'surge': {'value': 1.6},
                        'calculation_meta': common.JsonOverrideOverwrite(
                            {
                                'reason': 'pins_free',
                                'smooth': {
                                    'point_a': {
                                        'value': 1.0,
                                        'is_default': True,
                                    },
                                },
                            },
                        ),
                    },
                ],
            },  # expected_response_override
            common.JsonOverrideOverwrite([]),  # expected_resource_requests
            id='user_light_native',
        ),
        pytest.param(
            'price_calculation',  # intent
            True,  # enable_native_fallback
            False,  # has_surge_in_map
            False,  # surge_by_points_enabled
            True,  # forced_balance_enabled
            {'calculation_type': 'user_balance'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='user_balance_1_native',
        ),
        pytest.param(
            'price_calculation',  # intent
            True,  # enable_native_fallback
            False,  # has_surge_in_map
            True,  # surge_by_points_enabled
            True,  # forced_balance_enabled
            {'calculation_type': 'user_balance'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='user_balance_2_native',
        ),
        pytest.param(
            'price_calculation',  # intent
            True,  # enable_native_fallback
            True,  # has_surge_in_map
            True,  # surge_by_points_enabled
            True,  # forced_balance_enabled
            {
                'calculation_type': 'user_balance',
                'fallback_type': 'native_algorithm',
                'classes': [
                    {
                        'surge': {'value': 2.0},
                        'value_raw': 1.8,
                        'calculation_meta': {
                            'ps': 4.466666666666667,
                            'f_derivative': common.JsonOverrideDelete(),
                            'smooth': {
                                'point_a': {'value': 2.0, 'is_default': False},
                            },
                        },
                    },
                    {
                        # business
                    },
                    {
                        # comfortplus:
                        # affected by econom via weighted adjustment
                        'surge': {'value': 1.6},
                    },
                ],
            },  # expected_response_override
            [],  # expected_resource_requests_override
            id='user_balance_3_native',
        ),
        pytest.param(
            'surge_sampling',  # intent
            True,  # enable_native_fallback
            True,  # has_surge_in_map (irrelevant)
            True,  # surge_by_points_enabled (irrelevant)
            True,  # forced_balance_enabled (irrelevant)
            {
                'calculation_type': 'fixed_point',
                'fallback_type': 'native_algorithm',
                'classes': [
                    {
                        'surge': {'value': 2.0},
                        'value_raw': 1.8,
                        'calculation_meta': {
                            'ps': 4.466666666666667,
                            'f_derivative': common.JsonOverrideDelete(),
                            'smooth': {
                                'point_a': {'value': 2.0, 'is_default': False},
                            },
                        },
                    },
                    {
                        # business
                    },
                    {
                        # comfortplus:
                        # affected by econom via weighted adjustment
                        'surge': {'value': 1.6},
                    },
                ],
            },  # expected_response_override
            [],  # expected_resource_requests_override
            id='fixed_point_1_native',
        ),
        pytest.param(
            'surge_sampling',  # intent
            True,  # enable_native_fallback
            False,  # has_surge_in_map (irrelevant)
            True,  # surge_by_points_enabled (irrelevant)
            True,  # forced_balance_enabled (irrelevant)
            {'calculation_type': 'fixed_point'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='fixed_point_2_native',
        ),
        pytest.param(
            'surge_sampling',  # intent
            True,  # enable_native_fallback
            False,  # has_surge_in_map (irrelevant)
            False,  # surge_by_points_enabled (irrelevant)
            True,  # forced_balance_enabled (irrelevant)
            {'calculation_type': 'fixed_point'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='fixed_point_3_native',
        ),
        pytest.param(
            'surge_sampling',  # intent
            True,  # enable_native_fallback
            False,  # has_surge_in_map (irrelevant)
            False,  # surge_by_points_enabled (irrelevant)
            False,  # forced_balance_enabled (irrelevant)
            {'calculation_type': 'fixed_point'},  # expected_response_override
            [],  # expected_resource_requests_override
            id='fixed_point_4_native',
        ),
    ],
)
@pytest.mark.now('2020-07-06T19:21:49+03:00')
async def test_surge_by_points_basic(
        taxi_surge_calculator,
        heatmap_storage,
        mockserver,
        experiments3,
        taxi_config,
        enable_native_fallback,
        intent,
        has_surge_in_map,
        surge_by_points_enabled,
        forced_balance_enabled,
        expected_response_override,
        expected_resource_requests_override,
):
    if surge_by_points_enabled:
        experiments3.add_config(
            consumers=['surge-calculator/user'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[],
            name='surge_by_points_enabled',
            default_value={'value': True},
        )

    if forced_balance_enabled:
        experiments3.add_experiment(
            consumers=['surge-calculator/user'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[],
            name='force_balance_calculation',
            default_value={'value': True},
        )

    resource_requests = []

    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        request = request.json

        response = {'radius': 2785, 'generic': {}, 'reposition': {}}

        for category in request.get('allowed_classes', []):
            response['generic'][category] = {
                'free': 12,
                'on_order': 18,
                'free_chain': 3,
                'total': 30,
                'free_chain_groups': {'short': 3, 'medium': 3, 'long': 3},
            }

        request['__resource_name__'] = 'count_by_categories'
        request['allowed_classes'] = sorted(request['allowed_classes'])
        resource_requests.append(request)
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'}, json=response,
        )

    @mockserver.json_handler('/pin-storage/v1/get_stats/radius')
    def _add_pin_radius(request):
        request = dict(request.query)

        request['__resource_name__'] = 'get_stats/radius'
        request['categories'] = ','.join(
            sorted(request['categories'].split(',')),
        )
        resource_requests.append(request)

        categories = request['categories'].split(',')

        value_by_category = {'business': 1, 'comfortplus': 2, 'econom': 0}

        return {
            'stats': {
                'pins': 3,
                'pins_with_b': 0,
                'pins_with_order': 0,
                'pins_with_driver': 0,
                'prev_pins': 2.8800000000000003,
                'values_by_category': {
                    category: {
                        'estimated_waiting': value_by_category[category],
                        'pins_order_in_tariff': value_by_category[category],
                        'pins_driver_in_tariff': value_by_category[category],
                        'surge': value_by_category[category],
                    }
                    for category in categories
                },
                'global_pins': 3,
                'global_pins_with_order': 0,
                'global_pins_with_driver': 0,
            },
        }

    point_a = [37.752806233, 55.9]

    if has_surge_in_map:
        heatmap_storage.build_and_set_surge_map(
            cell_size_meter=500.123,
            envelope={
                'br': [point_a[0] - 0.00001, point_a[1] - 0.00001],
                'tl': [point_a[0] + 0.1, point_a[1] + 0.1],
            },
            values=SURGE_MAP_VALUES,
        )

    taxi_config.set_values(
        {'SURGE_NATIVE_FALLBACK_FORCE': enable_native_fallback},
    )

    if (
            enable_native_fallback
            and 'fallback_type' not in expected_response_override
    ):
        expected_response_override.update(
            {
                'fallback_type': 'native_algorithm',
                'classes': [
                    {
                        # econom
                        'value_raw': 1.8,
                        'surge': {'value': 1.8},
                        'calculation_meta': {
                            'ps': 4.466666666666667,
                            'f_derivative': common.JsonOverrideDelete(),
                            'smooth': {'point_a': {'value': 1.8}},
                        },
                    },
                    {
                        # business
                        'surge': {'value': 1.3},
                    },
                    {
                        # comfortplus
                        'surge': {'value': 1.5},
                    },
                ],
            },
        )

    await taxi_surge_calculator.invalidate_caches()

    request = {
        'user_id': 'a29e6a811131450f9a28337906594208',
        'classes': ['econom', 'business', 'comfortplus'],
        'point_a': point_a,
        'intent': intent,
    }
    expected_response = {
        'zone_id': 'Funtown',
        'user_layer': 'default',
        'experiment_id': 'e5d8a86361064b17833c3a42d7fd6b38',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'calculation_type': 'default',
        'is_cached': False,
        'classes': [
            {
                'name': 'econom',
                'value_raw': 1.5,
                'surge': {'value': 1.5},
                'calculation_meta': {
                    'counts': {
                        'free': 12,
                        'free_chain': 3,
                        'pins': 3,
                        'radius': 2785,
                        'total': 30,
                    },
                    'smooth': {'point_a': {'value': 1.5, 'is_default': True}},
                    'f_derivative': -0.056999999999999995,
                    'pins_meta': {
                        'pins_b': 0,
                        'pins_order': 0,
                        'pins_driver': 0,
                        'prev_pins': 2.8800000000000003,
                        'eta_in_tariff': 0.0,
                        'surge_in_tariff': 0.0,
                        'pins_order_in_tariff': 0,
                        'pins_driver_in_tariff': 0,
                    },
                    'ps': 8.836666666666668,
                    'reason': 'pins_free',
                },
            },
            {
                'name': 'business',
                'surge': {'value': 1.3},
                'value_raw': 1.3,
                'calculation_meta': {
                    'counts': {
                        'free': 12,
                        'free_chain': 3,
                        'pins': 3,
                        'radius': 2785,
                        'total': 30,
                    },
                    'smooth': {'point_a': {'value': 1.3, 'is_default': True}},
                    'pins_meta': {
                        'pins_b': 0,
                        'pins_order': 0,
                        'pins_driver': 0,
                        'prev_pins': 2.8800000000000003,
                        'eta_in_tariff': 1,
                        'surge_in_tariff': 1,
                        'pins_order_in_tariff': 1,
                        'pins_driver_in_tariff': 1,
                    },
                    'reason': 'pins_free',
                },
            },
            {
                'name': 'comfortplus',
                'surge': {'value': 1.4},
                'value_raw': 1.4,
                'calculation_meta': {
                    'counts': {
                        'free': 12,
                        'free_chain': 3,
                        'pins': 3,
                        'radius': 2785,
                        'total': 30,
                    },
                    'smooth': {'point_a': {'value': 1.4, 'is_default': True}},
                    'pins_meta': {
                        'pins_b': 0,
                        'pins_order': 0,
                        'pins_driver': 0,
                        'prev_pins': 2.8800000000000003,
                        'eta_in_tariff': 2,
                        'surge_in_tariff': 2,
                        'pins_order_in_tariff': 2,
                        'pins_driver_in_tariff': 2,
                    },
                    'reason': 'pins_free',
                },
            },
        ],
        'experiments': [],
        'experiment_errors': [],
    }

    expected_resource_requests = [
        {
            '__resource_name__': 'count_by_categories',
            'allowed_classes': ['business', 'comfortplus', 'econom'],
            'limit': 400,
            'max_distance': 2500,
            'point': point_a,
        },
        {
            '__resource_name__': 'get_stats/radius',
            'categories': 'business,comfortplus,econom',
            'point': '37.752806,55.900000',
            'radius': '2785.000000',
        },
    ]

    expected_response = common.json_override(
        expected_response, expected_response_override,
    )

    expected_resource_requests = common.json_override(
        expected_resource_requests, expected_resource_requests_override,
    )

    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)

    assert resource_requests == expected_resource_requests

    assert response.status == 200, response.text

    actual_response = response.json()
    calculation_id = actual_response.pop('calculation_id', '')

    assert len(calculation_id) == 32

    common.sort_data(expected_response)
    common.sort_data(actual_response)

    assert actual_response == expected_response
