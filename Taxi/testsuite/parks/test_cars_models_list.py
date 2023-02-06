import json

import pytest

ENDPOINT_URL = '/cars/models/list'


BAD_PARAMS = [
    (
        {
            'query': {
                'park': {'id': '1488'},
                'brand': {'name': 'unknown brand'},
            },
        },
        {'error': {'text': 'brand not found', 'code': 'car_brand_not_found'}},
    ),
    (
        {'query': {'park': {'id': '1488'}}},
        {'error': {'text': 'query.brand must be present'}},
    ),
]


OK_PARAMS = [
    (
        {
            'query': {
                'park': {'id': '1488'},
                'brand': {'name': 'Mercedes-Benz'},
            },
        },
        {'models': [{'name': 'AMG G63'}, {'name': 'SLR McLaren'}]},
    ),
    (
        {'query': {'park': {'id': '1488'}, 'brand': {'name': 'Pagani'}}},
        {'models': [{'name': 'Huayra'}]},
    ),
]


@pytest.mark.parametrize('request_json, expected_response', OK_PARAMS)
def test_ok(taxi_parks, request_json, expected_response):
    response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(request_json))

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize('request_json, expected_response', BAD_PARAMS)
def test_bad_request(taxi_parks, request_json, expected_response):
    response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(request_json))

    assert response.status_code == 400
    assert response.json() == expected_response
