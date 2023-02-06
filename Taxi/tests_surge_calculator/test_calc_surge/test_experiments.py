import json

import pytest

# pylint: disable=import-error
from . import common


@pytest.mark.config(ALL_CATEGORIES=['econom', 'business'])
async def test(taxi_surge_calculator, mockserver):
    candidates_request_count = 0

    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        nonlocal candidates_request_count
        candidates_request_count += 1
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'},
            json={
                'reposition': {},
                'generic': {
                    'econom': {
                        'total': 1,
                        'free': 0,
                        'on_order': 0,
                        'free_chain': 0,
                        'free_chain_groups': {
                            'short': 0,
                            'medium': 0,
                            'long': 0,
                        },
                    },
                    'business': {
                        'total': 1,
                        'free': 0,
                        'on_order': 0,
                        'free_chain': 0,
                        'free_chain_groups': {
                            'short': 0,
                            'medium': 0,
                            'long': 0,
                        },
                    },
                },
            },
        )

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
            {
                'name': 'econom',
                'calculation_meta': {
                    'counts': {
                        'total': 1,
                        'free': 0,
                        'free_chain': 0,
                        'pins': 0,
                        'radius': 1000,
                    },
                },
                'value_raw': 1.0,
                'surge': {'value': 5.0},
            },
            {
                'name': 'business',
                'calculation_meta': {
                    'counts': {
                        'total': 1,
                        'free': 0,
                        'free_chain': 0,
                        'pins': 0,
                        'radius': 1000,
                    },
                },
                'value_raw': 1.0,
                'surge': {'value': 11.0},
            },
        ],
        'experiments': [
            {
                'classes': [
                    {
                        'name': 'econom',
                        'calculation_meta': {
                            'counts': {
                                'total': 1,
                                'free': 0,
                                'free_chain': 0,
                                'pins': 0,
                                'radius': 1000,
                            },
                        },
                        'surge': {'value': 1.4},
                        'value_raw': 1.0,
                    },
                    {
                        'name': 'business',
                        'calculation_meta': {
                            'counts': {
                                'total': 1,
                                'free': 0,
                                'free_chain': 0,
                                'pins': 0,
                                'radius': 1000,
                            },
                        },
                        'surge': {'value': 1.0},
                        'value_raw': 1.0,
                    },
                ],
                'experiment_id': 'a29e6a811131450f9a28337906594208',
                'experiment_name': 'my_experiment',
            },
        ],
        'experiment_errors': [],
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    actual = response.json()

    assert len(actual.pop('calculation_id', '')) == 32

    common.sort_data(expected)
    common.sort_data(actual)

    assert actual == expected
    assert candidates_request_count == 1


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business'], REDUCE_CALC_SURGE_RESPONSE=True,
)
async def test_reduced_output(taxi_surge_calculator, mockserver):
    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'},
            json={
                'reposition': {},
                'generic': {
                    'econom': {
                        'total': 1,
                        'free': 0,
                        'on_order': 0,
                        'free_chain': 0,
                        'free_chain_groups': {
                            'short': 0,
                            'medium': 0,
                            'long': 0,
                        },
                    },
                    'business': {
                        'total': 1,
                        'free': 0,
                        'on_order': 0,
                        'free_chain': 0,
                        'free_chain_groups': {
                            'short': 0,
                            'medium': 0,
                            'long': 0,
                        },
                    },
                },
            },
        )

    request = {
        'point_a': [37.583369, 55.778821],
        'classes': ['econom', 'business'],
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    assert not response.json()['experiments']
    assert not response.json()['experiment_errors']


@pytest.mark.parametrize(
    'layer_meta, error',
    [
        pytest.param(
            {'name': 'default', 'suffix': ''},
            'at \'layer_meta\' missing required field \'separate_counts\'',
            id='missing required field',
        ),
        pytest.param(
            {'name': 'default', 'separate_counts': 1, 'suffix': ''},
            'at \'layer_meta.separate_counts\' '
            'expected \'boolean\', got \'integer\'',
            id='wrong type',
        ),
        pytest.param(
            {
                'name': 'default',
                'separate_counts': False,
                'suffix': '',
                'extra': 'field',
            },
            'at \'layer_meta\' no property named "extra" in object schema',
            id='extra field',
        ),
    ],
)
@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.pipeline('resource_params')
async def test_resource_params(
        taxi_surge_calculator, mockserver, layer_meta, error,
):
    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'},
            json={
                'reposition': {},
                'generic': {
                    'econom': {
                        'total': 1,
                        'free': 0,
                        'on_order': 0,
                        'free_chain': 0,
                        'free_chain_groups': {
                            'short': 0,
                            'medium': 0,
                            'long': 0,
                        },
                    },
                },
            },
        )

    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {'name': 'econom', 'value_raw': 1.0, 'surge': {'value': 7.0}},
        ],
        'experiments': [],
        'experiment_errors': [
            {
                'error': {
                    'message': (
                        f'JS runtime error: at 25:6 Error: '
                        f'request params for resource \'count_by_categories\' '
                        f'(field: \'candidates\') don\'t match resource\'s '
                        f'params-schema: {error}'
                    ),
                },
                'experiment_id': 'a29e6a811131450f9a28337906594208',
                'experiment_name': 'my_experiment',
            },
        ],
    }

    request = {
        'point_a': [37.583369, 55.778821],
        'classes': ['econom'],
        'user_id': json.dumps(layer_meta),
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200

    actual = response.json()
    actual.pop('calculation_id')
    common.sort_data(expected)
    common.sort_data(actual)

    assert actual == expected


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.pipeline('undefined_param')
async def test_undefined_param(taxi_surge_calculator, mockserver):
    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'},
            json={
                'reposition': {},
                'generic': {
                    'econom': {
                        'total': 1,
                        'free': 0,
                        'on_order': 0,
                        'free_chain': 0,
                        'free_chain_groups': {
                            'short': 0,
                            'medium': 0,
                            'long': 0,
                        },
                    },
                },
            },
        )

    request = {'point_a': [37.583369, 55.778821], 'classes': ['econom']}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200

    actual = response.json()
    actual.pop('calculation_id')

    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {'name': 'econom', 'value_raw': 4.4, 'surge': {'value': 4.0}},
        ],
        'experiments': [
            {
                'classes': [
                    {
                        'name': 'econom',
                        'value_raw': 3.3,
                        'surge': {'value': 3.0},
                    },
                ],
                'experiment_id': 'a29e6a811131450f9a28337906594208',
                'experiment_name': 'my_experiment',
            },
        ],
        'experiment_errors': [],
    }
    assert actual == expected


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.pipeline('modify_in_binding')
async def test_modify_in_binding(taxi_surge_calculator):
    request = {'point_a': [37.583369, 55.778821], 'classes': ['econom']}
    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {'name': 'econom', 'value_raw': 1.0, 'surge': {'value': 91.0}},
        ],
        'experiments': [],
        'experiment_errors': [
            {
                'error': {
                    'message': (
                        'JS runtime error: at 2:88 '
                        'at stage \'illegal_auto_init\': '
                        'Error: while setting '
                        'key \'name\'; to \'__output__.classes.econom\''
                        '; at stage \'illegal_auto_init\': '
                        '@__output__.classes.econom: object'
                        ' can be modified only inside transaction'
                    ),
                },
                'experiment_id': 'a29e6a811131450f9a28337906594208',
                'experiment_name': 'my_experiment',
            },
        ],
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    actual = response.json()
    assert response.status == 200

    actual.pop('calculation_id')
    common.sort_data(expected)
    common.sort_data(actual)
    assert actual == expected


@pytest.mark.pipeline('blocking_predicate')
@pytest.mark.config(ALL_CATEGORIES=['econom'])
async def test_dependent_stage(taxi_surge_calculator, mockserver):
    @mockserver.json_handler('/candidates/count-by-categories')
    def _count_by_categories(request):
        return mockserver.make_response(
            headers={'X-YaTaxi-Server-Hostname': 'mockserver'},
            json={
                'reposition': {},
                'generic': {
                    'econom': {
                        'total': 1,
                        'free': 0,
                        'on_order': 0,
                        'free_chain': 0,
                        'free_chain_groups': {
                            'short': 0,
                            'medium': 0,
                            'long': 0,
                        },
                    },
                },
            },
        )

    request = {'point_a': [37.583369, 55.778821], 'classes': ['econom']}
    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'is_cached': False,
        'classes': [
            {'name': 'econom', 'value_raw': 99.1, 'surge': {'value': 81.2}},
        ],
        'experiments': [
            {
                'classes': [
                    {
                        'name': 'econom',
                        'value_raw': 99.1,
                        'surge': {'value': 81.2},
                    },
                ],
                'experiment_id': 'a29e6a811131450f9a28337906594208',
                'experiment_name': 'my_experiment',
            },
        ],
        'experiment_errors': [],
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    actual = response.json()
    assert response.status == 200

    actual.pop('calculation_id')
    common.sort_data(expected)
    common.sort_data(actual)
    assert actual == expected


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.pipeline('condition_hierarchy')
async def test_condition_hierarchy(taxi_surge_calculator):
    request = {'point_a': [37.583369, 55.778821], 'classes': ['econom']}
    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {'name': 'econom', 'value_raw': 2.0, 'surge': {'value': 22.0}},
        ],
        'experiments': [
            {
                'classes': [
                    {
                        'name': 'econom',
                        'value_raw': 2.0,
                        'surge': {'value': 22.0},
                    },
                ],
                'experiment_id': 'a29e6a811131450f9a28337906594208',
                'experiment_name': 'my_experiment',
            },
        ],
        'experiment_errors': [],
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    actual = response.json()
    assert response.status == 200

    actual.pop('calculation_id')
    common.sort_data(expected)
    common.sort_data(actual)
    assert actual == expected
