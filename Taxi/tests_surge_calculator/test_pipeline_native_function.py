import json

import pytest

# EXAMPLE: '.native_function_{name}.json'
# NOTE: should be empty if for merge
ACTUAL_RESPONSE_DUMP_LOCATION_TPL = ''
INVALID_CONSUMER_ERROR_CODE = 'invalid_consumer'
NOT_FOUND_ERROR_CODE = 'NOT_FOUND'


@pytest.mark.parametrize('name', ['initialize', 'round'])
async def test_native_function(taxi_surge_calculator, load_json, name):
    response = await taxi_surge_calculator.get(
        'v1/js/pipeline/native-function',
        params={'consumer': 'taxi-surge', 'name': name},
    )
    assert response.status_code == 200
    data = response.json()
    expected = load_json(f'expected_response.{name}.json')

    if ACTUAL_RESPONSE_DUMP_LOCATION_TPL:
        json.dump(
            data,
            open(ACTUAL_RESPONSE_DUMP_LOCATION_TPL.format(name=name), 'w+'),
            ensure_ascii=False,
            indent=2,
        )
        assert False, 'response dump enabled'

    assert data == expected


async def test_native_function_unknown_consumer(taxi_surge_calculator):
    response = await taxi_surge_calculator.get(
        'v1/js/pipeline/native-function',
        params={'consumer': 'something-not-existing', 'name': 'initialize'},
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == INVALID_CONSUMER_ERROR_CODE


async def test_native_function_unknown_function(taxi_surge_calculator):
    response = await taxi_surge_calculator.get(
        'v1/js/pipeline/native-function',
        params={'consumer': 'taxi-surge', 'name': 'something-not-existing'},
    )
    assert response.status_code == 404
    response_json = response.json()
    assert response_json['code'] == NOT_FOUND_ERROR_CODE
