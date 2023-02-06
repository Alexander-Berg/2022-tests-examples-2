import json

import pytest


def _result_key(result):
    return result['calculator_name']


def _calc_result_key(result):
    return result['place_id'] + result.get('delivery_zone_id', 9999)


def _error_key(error):
    return error['place_id'] + error.get('delivery_zone_id', 9999)


def _sort_response(response):
    response['errors'].sort(key=_error_key)
    for item in response['results']:
        item['results'].sort(key=_calc_result_key)
    response['results'].sort(key=_result_key)


@pytest.mark.pipeline('access_not_existing_in_input')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_access_not_existing_in_input(taxi_eda_surge_calculator):
    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    expected_response = {
        'results': [],
        'errors': [
            {
                'place_id': 1,
                'error_message': (
                    'Error while executing calc_surge pipeline: '
                    'At pipeline "calc_surge" at stage "first" '
                    'at input with top query "not_existing": '
                    'no property named "not_existing" in object schema'
                ),
            },
        ],
    }
    response = response.json()
    _sort_response(response)
    _sort_response(expected_response)
    assert response == expected_response


@pytest.mark.pipeline('access_before_assignment')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_access_before_assignment(taxi_eda_surge_calculator):
    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    expected_response = {
        'results': [],
        'errors': [
            {
                'place_id': 1,
                'error_message': (
                    'Error while executing calc_surge pipeline: '
                    'At pipeline "calc_surge" at stage "use_value" '
                    'at input with top query "places_out": '
                    'output won\'t be available here'
                ),
            },
        ],
    }
    response = response.json()
    _sort_response(response)
    _sort_response(expected_response)
    assert response == expected_response


@pytest.mark.pipeline('access_object_field')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_access_object_field(taxi_eda_surge_calculator):
    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    expected_response = {
        'results': [
            {
                'calculator_name': 'calc_surge',
                'results': [{'place_id': 1, 'result': {'total': 1}}],
            },
        ],
        'errors': [],
    }
    response = response.json()
    _sort_response(response)
    _sort_response(expected_response)
    assert response == expected_response


@pytest.mark.pipeline('invalid_output_assignment')
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_invalid_output_assignment(taxi_eda_surge_calculator):
    await taxi_eda_surge_calculator.invalidate_caches()
    data = {'place_ids': [1, 2]}
    response = await taxi_eda_surge_calculator.post(
        'v1/calc-surge', data=json.dumps(data),
    )
    assert response.status_code == 200
    expected_response = {
        'results': [
            {
                'calculator_name': 'calc_surge',
                'results': [
                    {'place_id': 1, 'result': {'total': 1}},
                    {'place_id': 2, 'result': {'total': 2}},
                ],
            },
        ],
        'errors': [],
    }
    response = response.json()
    _sort_response(response)
    _sort_response(expected_response)
    assert response == expected_response
