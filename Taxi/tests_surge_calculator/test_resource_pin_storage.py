# pylint: disable=E1101,W0612
import json
import math

import pytest  # noqa: F401


@pytest.mark.config(ALL_CATEGORIES=['econom'])
async def test_missing_params(taxi_surge_calculator):
    # missing args
    request = {'point_a': [38.0, 51]}
    expected = {'code': '500', 'message': 'Internal Server Error'}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 500
    data = response.json()

    assert data == expected


@pytest.mark.parametrize(
    'storage_request, layer_meta, expected_code,'
    'expected_request, expected_count_pins',
    [
        pytest.param(
            {'args': 42},
            None,
            500,
            None,
            None,
            id='invalid input (non-object)',
        ),
        pytest.param(
            {'point': [4.56, 1.23]},
            None,
            500,
            None,
            None,
            id='invalid (point + no radius)',
        ),
        pytest.param(
            {'radius': 1000},
            None,
            500,
            None,
            None,
            id='invalid (no point + radius)',
        ),
        pytest.param(
            {'point': [4.56, 1.23], 'radius': 1000},
            None,
            200,
            {'point': '4.560000,1.230000', 'radius': '1000.000000'},
            1,
            id='valid (radius)',
        ),
        pytest.param(
            {
                'point': [4.56, 1.23],
                'radius': 1000,
                'graph_points': 10,
                'graph_distance': 1500,
            },
            None,
            200,
            {
                'point': '4.560000,1.230000',
                'radius': '1000.000000',
                'graph_points': '10',
                'graph_distance': '1500.000000',
            },
            1,
            id='valid (radius); graph parameters',
        ),
        pytest.param(
            {'point': [4.56, 1.23], 'radius': 1000},
            {'name': 'default', 'separate_counts': False, 'suffix': ''},
            200,
            {'point': '4.560000,1.230000', 'radius': '1000.000000'},
            1,
            id='valid (radius) default; no separate counts',
        ),
        pytest.param(
            {'point': [4.56, 1.23], 'radius': 1000},
            {'name': 'default', 'separate_counts': True, 'suffix': ''},
            200,
            {
                'point': '4.560000,1.230000',
                'radius': '1000.000000',
                'user_layer': 'default',
            },
            1,
            id='valid (radius) default; separate counts',
        ),
        pytest.param(
            {'point': [4.56, 1.23], 'radius': 1000},
            {'name': 'alternative', 'separate_counts': False, 'suffix': ''},
            200,
            {'point': '4.560000,1.230000', 'radius': '1000.000000'},
            1,
            id='valid (radius) alternative; no separate counts',
        ),
        pytest.param(
            {'point': [4.56, 1.23], 'radius': 1000},
            {'name': 'alternative', 'separate_counts': True, 'suffix': ''},
            200,
            {
                'point': '4.560000,1.230000',
                'radius': '1000.000000',
                'user_layer': 'alternative',
            },
            1,
            id='valid (radius) alternative; separate counts',
        ),
    ],
)
@pytest.mark.config(ALL_CATEGORIES=['econom'])
async def test_get_stats(
        taxi_surge_calculator,
        mockserver,
        storage_request,
        layer_meta,
        expected_code,
        expected_request,
        expected_count_pins,
):
    actual_request = None

    @mockserver.json_handler('/pin-storage/v1/get_stats')
    def _get_stats(request):
        nonlocal actual_request
        actual_request = request.args
        return {
            'stats': {
                'pins': 0,
                'pins_with_b': 0,
                'pins_with_order': 0,
                'pins_with_driver': 0,
                'prev_pins': 0,
                'values_by_category': {},
                'global_pins': 0,
                'global_pins_with_order': 0,
                'global_pins_with_driver': 0,
            },
        }

    @mockserver.json_handler('/pin-storage/v1/get_stats/radius')
    def _get_stats_radius(request):
        nonlocal actual_request
        actual_request = request.args
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

    resource_params = {'request': storage_request, 'layer_meta': layer_meta}
    request = {'point_a': [38.1, 51], 'user_id': json.dumps(resource_params)}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == expected_code
    data = response.json()
    if expected_code == 500:
        expected = {'code': '500', 'message': 'Internal Server Error'}
        assert data == expected
    else:
        actual_counts = data['classes'][0]['calculation_meta']['counts']
        expected_counts = {
            'pins': expected_count_pins,
            'free': 0,
            'free_chain': 0,
            'total': 0,
            'radius': 0,
        }
        assert actual_counts == expected_counts
        assert actual_request == expected_request


@pytest.mark.now('2021-01-28T17:05:00.00000+0300')
@pytest.mark.pipeline('graph_points')
@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    SURGE_CALCULATOR_PIN_STATS_WEIGHT_PARAMS=dict(
        weight_time_correction=1, query_time=600, time_shift=300,
    ),
)
async def test_graph_points(taxi_surge_calculator, mockserver):
    fixed_points = [
        {'position_id': 'geoid{}'.format(i), 'distance': distance}
        for i, distance in enumerate([10, 20, 30])
    ]

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
                'graph_fixed_points': fixed_points,
            },
        }

    response = await taxi_surge_calculator.post(
        '/v1/calc-surge',
        json={'point_a': [38.1, 51.2], 'user_id': 'someoneunknown'},
    )

    assert response.status == 200
    actual = response.json()
    actual.pop('calculation_id')

    enriched_points = actual['classes'][0]['calculation_meta']['reason']
    enriched_points = json.loads(enriched_points)
    actual['classes'][0]['calculation_meta'].pop('reason')

    # equation: exp(-(t * 1 / 600) ** 2)
    # weight for shifted in 5 minutes pin: exp(-((5 * 60) * 1 / 600)**2)
    # geoid0:
    #     17:00 - surge=10, pins=5
    #     17:05 - surge=20, pins=50
    # geoid1:
    #     16:59 - will be discarded, because too old
    #     17:05 - surge=15, pins=10
    # geoid2:
    #     no corresponding calculations in cache
    k = math.exp(-(((5 * 60) * 1 / 600) ** 2))
    enriched_points.sort(key=lambda t: t['position_id'])
    assert enriched_points == [
        {
            'position_id': 'geoid0',
            'distance': 10,
            'tags': ['cause', 'ami'],
            'surge_value': (20 + 10 * k) / (1 + k),
            'surge_value_shifted': (20 * k + 10) / (k + 1),
            'pins': (50 + 5 * k) / (1 + k),
            'pins_shifted': (50 * k + 5) / (k + 1),
        },
        {
            'position_id': 'geoid1',
            'distance': 20,
            'tags': ['feel', 'this', 'way'],
            'surge_value': 15,
            'surge_value_shifted': 15,
            'pins': 10,
            'pins_shifted': 10,
        },
    ]

    expected = {
        'zone_id': 'test_id',
        'user_layer': 'default',
        'experiment_id': 'test_production_experiment_id',
        'experiment_name': '<unnamed experiment>',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {
                'name': 'econom',
                'value_raw': 36,
                'surge': {'value': 15},
                'calculation_meta': {
                    'counts': {
                        'free': 0,
                        'free_chain': 0,
                        'pins': 1,
                        'radius': 0,
                        'total': 0,
                    },
                },
            },
        ],
        'experiments': [],
        'experiment_errors': [],
    }
    assert actual == expected
