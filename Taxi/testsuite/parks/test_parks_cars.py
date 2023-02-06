import json

import pytest

from taxi_tests.utils import ordered_object


OK_PARAMS = [
    ({'query': {'park': {'id': ['net_takogo']}}}, 'response_empty.json'),
    ({'query': {'park': {'id': ['1234abc']}}}, 'response_ok.json'),
    (
        {
            'query': {
                'car': {
                    'id': [
                        '00033693fa67429588f09de95f4aaa9c',
                        '005c49c5f2fb4075a3fbd015ebace10e',
                    ],
                },
            },
        },
        'response_ok.json',
    ),
    (
        {'query': {'park': {'id': ['chair_yandex_brand']}}},
        'response_chair_yandex_brand.json',
    ),
    (
        {'query': {'park': {'id': ['chair_empty_brand']}}},
        'response_chair_empty_brand.json',
    ),
    (
        {'query': {'park': {'id': ['chair_isofix']}}},
        'response_chair_isofix.json',
    ),
    (
        {'offset': 2, 'query': {'park': {'id': ['1234abc']}}},
        'response_empty.json',
    ),
    (
        {'limit': 10, 'offset': 2, 'query': {'park': {'id': ['1234abc']}}},
        'response_empty.json',
    ),
    (
        {'limit': 10, 'offset': 10, 'query': {'park': {'id': ['1234abc']}}},
        'response_empty.json',
    ),
    (
        {'limit': 1, 'offset': 0, 'query': {'park': {'id': ['1234abc']}}},
        'response_ok_005.json',
    ),
    (
        {'limit': 1, 'offset': 1, 'query': {'park': {'id': ['1234abc']}}},
        'response_ok_00033.json',
    ),
    (
        {'limit': 10, 'offset': 1, 'query': {'park': {'id': ['1234abc']}}},
        'response_ok_00033.json',
    ),
    (
        {'limit': 2, 'offset': 0, 'query': {'park': {'id': ['1234abc']}}},
        'response_ok.json',
    ),
]


@pytest.mark.parametrize('request_json,expected_response', OK_PARAMS)
def test_ok(taxi_parks, load_json, request_json, expected_response):
    response = taxi_parks.post('/parks/cars', data=json.dumps(request_json))

    assert response.status_code == 200, response.text
    expected_json = load_json(expected_response)
    if 'limit' not in request_json:
        expected_json.pop('has_more', None)

    ordered_object.assert_eq(
        response.json(),
        expected_json,
        [
            'cars',
            'cars.category',
            'cars.amenities',
            'cars.chairs',
            'cars.chairs.categories',
            'cars.confirmed_chairs',
            'cars.confirmed_chairs.categories',
            'cars.confirmed_chairs.confirmed_categories',
            'cars.tags',
        ],
    )


def test_bad_request(taxi_parks):
    response = taxi_parks.post('/parks/cars')

    assert response.status_code == 400
    assert response.json() == {
        'error': {'text': 'request must be in json format'},
    }
