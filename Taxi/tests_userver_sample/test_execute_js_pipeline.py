# -*- coding: utf-8 -*-
import pytest


async def test_execute_js_pipeline(taxi_userver_sample):
    request = {
        'pipeline': 'default',
        'input': {
            'place_ids': ['1', '2'],
            'places_settings': {
                '1': {'data': 'settings data for 1'},
                '2': {'data': 'settings data for 2'},
            },
            'coeff': 2.1,
        },
    }
    expected = {
        'places': [
            {
                'id': '1',
                'settings': {'data': 'settings data for 1'},
                'coeff': 2.1,
                'data_from_resource': {
                    'params': {'fetch_arg_1': 1, 'fetch_arg_2': 'str'},
                    'string_field': 'data from string field',
                    'number_field': 1.5,
                    'integer_field': 42,
                    'inner_string_field': 'data from inner string field',
                    'inner_number_field': 2.5,
                    'inner_integer_field': 25,
                },
            },
            {
                'id': '2',
                'settings': {'data': 'settings data for 2'},
                'coeff': 2.1,
                'data_from_resource': {
                    'params': {'fetch_arg_1': 1, 'fetch_arg_2': 'str'},
                    'string_field': 'data from string field',
                    'number_field': 1.5,
                    'integer_field': 42,
                    'inner_string_field': 'data from inner string field',
                    'inner_number_field': 2.5,
                    'inner_integer_field': 25,
                },
            },
        ],
    }

    response = await taxi_userver_sample.post(
        'execute-js-pipeline', json=request,
    )
    assert response.status_code == 200
    assert response.encoding == 'utf-8'
    assert response.json() == expected


async def test_execute_js_pipeline_non_blocking(taxi_userver_sample):
    request = {
        'pipeline': 'non_blocking',
        'input': {
            'place_ids': ['1', '2'],
            'places_settings': {
                '1': {'data': 'settings data for 1'},
                '2': {'data': 'settings data for 2'},
            },
            'coeff': 2.1,
        },
    }
    expected = {
        'places': [
            {
                'id': '1',
                'settings': {'data': 'settings data for 1'},
                'coeff': 2.1,
                'data_from_resource': {
                    'params': {'fetch_arg_1': 1, 'fetch_arg_2': 'str'},
                    'string_field': 'data from string field [non-blocking]',
                    'number_field': 1.7,
                    'integer_field': 40,
                    'inner_string_field': (
                        'data from inner string field [non-blocking]'
                    ),
                    'inner_number_field': 2.6,
                    'inner_integer_field': 26,
                },
            },
            {
                'id': '2',
                'settings': {'data': 'settings data for 2'},
                'coeff': 2.1,
                'data_from_resource': {
                    'params': {'fetch_arg_1': 1, 'fetch_arg_2': 'str'},
                    'string_field': 'data from string field [non-blocking]',
                    'number_field': 1.7,
                    'integer_field': 40,
                    'inner_string_field': (
                        'data from inner string field [non-blocking]'
                    ),
                    'inner_number_field': 2.6,
                    'inner_integer_field': 26,
                },
            },
        ],
    }

    response = await taxi_userver_sample.post(
        'execute-js-pipeline', json=request,
    )
    assert response.status_code == 200
    assert response.encoding == 'utf-8'
    assert response.json() == expected


async def test_cached_resource(taxi_userver_sample):
    request = {'pipeline': 'use_cache', 'input': {}}
    response = await taxi_userver_sample.post(
        'execute-js-pipeline', json=request,
    )
    assert response.status_code == 200
    cached_value = response.json()['value']

    await taxi_userver_sample.run_periodic_task('cachable_resource_update')
    response = await taxi_userver_sample.post(
        'execute-js-pipeline', json=request,
    )
    expected = {'value': cached_value}

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize(
    'pipeline_name,code_range,error',
    [
        (
            'bad_script_4',
            'at stage \'bad_script_compute_with_undefined\'',
            'ReferenceError: undefined_variable is not defined',
        ),
    ],
)
async def test_execute_js_pipeline_bad_path(
        taxi_userver_sample, pipeline_name, error, code_range,
):
    request = {'pipeline': pipeline_name, 'input': {}}
    response = await taxi_userver_sample.post(
        'execute-js-pipeline', json=request,
    )
    assert response.status_code == 500
    assert error in response.text
    assert code_range in response.text


async def test_execute_js_pipeline_resource_aliases(taxi_userver_sample):
    request = {
        'pipeline': 'resource_aliases',  # from db_eda_surge_pipelines.json
        'input': {'values': ['A', 'B', 'C', 'D', 'E']},
    }
    expected = {
        'result': {
            'r0': 'A',
            'r1': 'B',
            'r2': 'C',
            'r3': 'D',
            'r4': 'E',
            'r5': 'non-field params non-blocking',
            'r6': 'non-field params blocking',
        },
    }

    response = await taxi_userver_sample.post(
        'execute-js-pipeline', json=request,
    )

    assert response.status_code == 200
    assert response.encoding == 'utf-8'
    assert response.json() == expected


async def test_execute_js_pipeline_metrics(
        taxi_userver_sample, taxi_userver_sample_monitor,
):
    test_pipeline = 'resource_metrics'  # from db_eda_surge_pipelines.json
    test_resource = 'sample_resource'  # from db_eda_surge_pipelines.json
    request = {'pipeline': test_pipeline, 'input': {}}
    response = await taxi_userver_sample.post(
        'execute-js-pipeline', json=request,
    )

    assert response.status_code == 200
    assert response.encoding == 'utf-8'

    response = await taxi_userver_sample_monitor.get('')

    assert response.status_code == 200
    assert response.encoding == 'utf-8'
    data = response.json()
    resource = data['js-pipeline-resource-management']['resources'][
        test_resource
    ]
    percentiles = {
        'p50',
        'p75',
        'p80',
        'p85',
        'p90',
        'p95',
        'p98',
        'p99',
        'p100',
    }
    assert resource['1min']['error']['count'] == 0
    assert resource['1min']['success']['count'] > 0  # +1 for each pipeline ref
    assert all(i in resource['1min']['success']['time'] for i in percentiles)


@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'user_id,expected',
    [
        (1, {'user': {'id': 1}}),
        (42, {'user': {'id': 42, 'is_even_test_result': False}}),
    ],
)
async def test_execute_js_pipeline_predicate(
        taxi_userver_sample, user_id, expected,
):
    request = {
        'pipeline': 'conditions_and_predicates',
        'input': {'user_id': user_id},
    }

    response = await taxi_userver_sample.post(
        'execute-js-pipeline', json=request,
    )
    assert response.status_code == 200
    assert response.encoding == 'utf-8'
    assert response.json() == expected
