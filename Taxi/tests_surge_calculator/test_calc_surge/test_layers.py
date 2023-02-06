import pytest

from . import common


@pytest.mark.config(ALL_CATEGORIES=['econom', 'business'])
@pytest.mark.parametrize(
    'mode,experiment_data_override,expected_override,'
    'expected_resource_request_sets,no_alternative',
    [
        ('disabled', None, None, ['both'], False),
        (
            'disabled',
            {'default_value': {'surge_layer': 'alternative'}},
            {'user_layer': 'alternative'},
            ['both'],
            False,
        ),
        ('background', None, None, ['both', 'alternative'], False),
        (
            'background',
            {'default_value': {'surge_layer': 'alternative'}},
            {'user_layer': 'alternative'},
            ['both', 'alternative'],
            False,
        ),
        ('enabled', None, None, ['default', 'alternative'], False),
        (
            'enabled',
            {'default_value': {'surge_layer': 'alternative'}},
            {
                'user_layer': 'alternative',
                'experiment_id': 'a29e6a811131450f9a28337906594208',
                'experiment_name': 'my_experiment',
                'experiment_layer': 'alternative',
                'is_cached': False,
                'classes': [
                    {
                        'name': 'econom',
                        'surge': {'value': 1.4},
                        'value_raw': 1.0,
                    },
                    {
                        'name': 'business',
                        'surge': {'value': 1.0},
                        'value_raw': 1.0,
                    },
                ],
                'experiments': [
                    {
                        'classes': [
                            {
                                'name': 'econom',
                                'value_raw': 1.0,
                                'surge': {'value': 5.0},
                            },
                            {
                                'name': 'business',
                                'value_raw': 1.0,
                                'surge': {'value': 11.0},
                            },
                        ],
                        'experiment_id': 'a29e6a811131450f9a28337906594207',
                        'experiment_name': 'default',
                        'experiment_layer': 'default',
                    },
                ],
                'experiment_errors': [],
            },
            ['default', 'alternative'],
            False,
        ),
        (
            'enabled',
            {'default_value': {'surge_layer': 'alternative'}},
            {
                'user_layer': 'alternative',
                'experiment_layer': 'alternative',
                'is_cached': False,
                'classes': [
                    {
                        'name': 'econom',
                        'value_raw': 1.0,
                        'surge': {'value': 5.0},
                    },
                    {
                        'name': 'business',
                        'value_raw': 1.0,
                        'surge': {'value': 11.0},
                    },
                ],
                'experiments': [
                    {
                        'classes': [
                            {
                                'name': 'econom',
                                'value_raw': 1.0,
                                'surge': {'value': 5.0},
                            },
                            {
                                'name': 'business',
                                'value_raw': 1.0,
                                'surge': {'value': 11.0},
                            },
                        ],
                        'experiment_id': 'a29e6a811131450f9a28337906594207',
                        'experiment_name': 'default',
                        'experiment_layer': 'default',
                    },
                    {
                        'classes': [
                            {
                                'name': 'econom',
                                'surge': {'value': 1.4},
                                'value_raw': 1.0,
                            },
                            {
                                'name': 'business',
                                'surge': {'value': 1.0},
                                'value_raw': 1.0,
                            },
                        ],
                        'experiment_id': 'a29e6a811131450f9a28337906594208',
                        'experiment_name': 'my_experiment',
                    },
                ],
                'experiment_errors': [],
            },
            ['default', 'alternative'],
            True,
        ),
    ],
)
async def test(
        taxi_surge_calculator,
        mockserver,
        experiments3,
        taxi_config,
        admin_surger,
        experiment_data_override,
        mode,
        expected_override,
        expected_resource_request_sets,
        no_alternative,
):
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

        return {
            'stats': {
                'pins': 3,
                'pins_with_b': 0,
                'pins_with_order': 0,
                'pins_with_driver': 0,
                'prev_pins': 2.8800000000000003,
                'values_by_category': {
                    'business': {
                        'estimated_waiting': 0,
                        'surge': 0,
                        'pins_order_in_tariff': 0,
                        'pins_driver_in_tariff': 0,
                    },
                },
                'global_pins': 3,
                'global_pins_with_order': 0,
                'global_pins_with_driver': 0,
            },
        }

    experiment_data = dict(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='ghost_city',
        consumers=['surge-calculator/user', 'surge-calculator/layer'],
        clauses=[
            {
                'predicate': {
                    'init': {
                        'arg_name': 'layer',
                        'arg_type': 'string',
                        'value': 'default',
                    },
                    'type': 'eq',
                },
                'title': 'default layer',
                'value': {'surge_layer': 'default'},
            },
            {
                'predicate': {
                    'init': {
                        'arg_name': 'layer',
                        'arg_type': 'string',
                        'value': 'alternative',
                    },
                    'type': 'eq',
                },
                'title': 'alternative layer',
                'value': {'surge_layer': 'alternative'},
            },
        ],
        default_value={'surge_layer': 'default'},
    )

    if no_alternative:
        for zone in admin_surger.zones.values():
            zone['alternative_experiment_id'] = None

    if experiment_data_override:
        experiment_data.update(experiment_data_override)

    experiments3.add_experiment(**experiment_data)
    taxi_config.set_values(
        dict(
            SURGE_ALTERNATIVE_LAYERS={
                '__default__': {
                    'layers': {'alternative': {'mode': mode}},
                    'experiment_name': 'ghost_city',
                },
            },
        ),
    )

    await taxi_surge_calculator.invalidate_caches()

    request = {
        'point_a': [37.583369, 55.778821],
        'classes': ['econom', 'business'],
    }

    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {'name': 'econom', 'value_raw': 1.0, 'surge': {'value': 5.0}},
            {'name': 'business', 'value_raw': 1.0, 'surge': {'value': 11.0}},
        ],
        'experiments': [
            {
                'classes': [
                    {
                        'name': 'econom',
                        'surge': {'value': 1.4},
                        'value_raw': 1.0,
                    },
                    {
                        'name': 'business',
                        'surge': {'value': 1.0},
                        'value_raw': 1.0,
                    },
                ],
                'experiment_id': 'a29e6a811131450f9a28337906594208',
                'experiment_name': 'my_experiment',
                'experiment_layer': 'alternative',
            },
        ],
        'experiment_errors': [],
    }

    known_resource_request_sets = {
        'alternative': [
            {
                '__resource_name__': 'count_by_categories',
                'allowed_classes': ['business', 'econom'],
                'limit': 400,
                'max_distance': 2500,
                'metadata': {
                    'experiments': [
                        {
                            'is_signal': False,
                            'name': 'ghost_city',
                            'position': 1,
                            'value': {'surge_layer': 'alternative'},
                            'version': 1,
                        },
                    ],
                },
                'point': [37.583369, 55.778821],
                'required_experiments': ['ghost_city'],
            },
            {
                '__resource_name__': 'get_stats/radius',
                'categories': 'business,econom',
                'point': '37.583369,55.778821',
                'radius': '2785.000000',
                'user_layer': 'alternative',
            },
        ],
        'default': [
            {
                '__resource_name__': 'count_by_categories',
                'allowed_classes': ['business', 'econom'],
                'limit': 400,
                'max_distance': 2500,
                'metadata': {
                    'experiments': [
                        {
                            'is_signal': False,
                            'name': 'ghost_city',
                            'position': 0,
                            'value': {'surge_layer': 'default'},
                            'version': 1,
                        },
                    ],
                },
                'point': [37.583369, 55.778821],
                'required_experiments': ['ghost_city'],
            },
            {
                '__resource_name__': 'get_stats/radius',
                'categories': 'business,econom',
                'point': '37.583369,55.778821',
                'radius': '2785.000000',
                'user_layer': 'default',
            },
        ],
        'both': [
            {
                '__resource_name__': 'count_by_categories',
                'allowed_classes': ['business', 'econom'],
                'limit': 400,
                'max_distance': 2500,
                'point': [37.583369, 55.778821],
            },
            {
                '__resource_name__': 'get_stats/radius',
                'categories': 'business,econom',
                'point': '37.583369,55.778821',
                'radius': '2785.000000',
            },
        ],
    }

    expected_resource_requests = []

    for resource_request_set in expected_resource_request_sets:
        expected_resource_requests.extend(
            known_resource_request_sets[resource_request_set],
        )

    if expected_override:
        expected.update(expected_override)

    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    actual = response.json()

    assert len(actual.pop('calculation_id', '')) == 32

    common.sort_data(expected)
    common.sort_data(actual)

    assert actual == expected
    assert (
        common.sort_list_by_list(resource_requests, expected_resource_requests)
        == expected_resource_requests
    )
