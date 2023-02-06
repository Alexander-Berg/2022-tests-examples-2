import json

# NOTE: should be empty if for merge
ACTUAL_RESPONSE_DUMP_LOCATION = ''
INVALID_CONSUMER_ERROR_CODE = 'invalid_consumer'


def sorted_by_name(response: dict):
    return {
        'functions': sorted(
            response['functions'], key=lambda item: item['name'],
        ),
    }


async def test_native_functions_list(taxi_surge_calculator, load_json):
    response = await taxi_surge_calculator.get(
        'v1/js/pipeline/native-functions-list',
        params={'consumer': 'taxi-surge'},
    )
    assert response.status_code == 200
    data = sorted_by_name(response.json())
    expected = sorted_by_name(load_json('expected_response.json'))

    if ACTUAL_RESPONSE_DUMP_LOCATION:
        json.dump(
            data,
            open(ACTUAL_RESPONSE_DUMP_LOCATION, 'w+'),
            ensure_ascii=False,
            indent=2,
        )
        assert False, 'response dump enabled'

    assert data == expected


async def test_native_functions_list_unknown_consumer(taxi_surge_calculator):
    response = await taxi_surge_calculator.get(
        'v1/js/pipeline/native-functions-list',
        params={'consumer': 'something-not-existing'},
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == INVALID_CONSUMER_ERROR_CODE
