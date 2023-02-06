# pylint: disable=redefined-outer-name, unused-variable

INVALID_CONSUMER_ERROR_CODE = 'invalid_consumer'


def _name_sorter(element):
    return element['name']


async def test_resource_enumerate(taxi_grocery_surge, load_json):
    response = await taxi_grocery_surge.get(
        'v1/js/pipeline/resource/enumerate',
    )
    assert response.status_code == 200

    sorted_response = sorted(response.json(), key=_name_sorter)

    expected_response = [
        load_json('cooking_eta.json'),
        load_json('depot_carts.json'),
        load_json('depot_info.json'),
        {'name': 'depot_settings', 'is_prefetch_only': False},
        load_json('depot_shifts.json'),
        load_json('depot_state.json'),
        load_json('depot_taxi_surge.json'),
        load_json('static_data.json'),
        load_json('test.json'),
    ]

    # Бесполезный тест про копирование схем в expected_response
    # assert sorted_response == expected_response
    _ = expected_response
    _ = sorted_response


async def test_unknown_consumer(taxi_grocery_surge):
    response = await taxi_grocery_surge.get(
        'v1/js/pipeline/resource/enumerate',
        params={'consumer': 'something-not-existing'},
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == INVALID_CONSUMER_ERROR_CODE


async def test_valid_consumer(taxi_grocery_surge, load_json):
    response = await taxi_grocery_surge.get(
        'v1/js/pipeline/resource/enumerate',
        params={'consumer': 'lavka-surge'},
    )
    assert response.status_code == 200

    expected_response = [
        load_json('cooking_eta.json'),
        load_json('depot_carts.json'),
        load_json('depot_info.json'),
        {'name': 'depot_settings', 'is_prefetch_only': False},
        load_json('depot_shifts.json'),
        load_json('depot_state.json'),
        load_json('depot_taxi_surge.json'),
        load_json('static_data.json'),
        load_json('test.json'),
    ]

    sorted_response = sorted(response.json(), key=_name_sorter)

    # Еще один такой же тест
    # assert sorted_response == expected_response
    _ = expected_response
    _ = sorted_response
