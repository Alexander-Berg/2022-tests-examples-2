import json

import pytest

from . import auth
from . import utils

MOCK_URL = '/parks/cars/list'
ENDPOINT_URL = '/v1/parks/cars/list'


LIST_REQUEST = {
    'query': {'park': {'id': 'xxx', 'car': {'id': ['1']}}},
    'limit': 2,
}

PARKS_REQUEST = {
    'query': {'park': {'id': 'xxx', 'car': {'id': ['1']}}},
    'fields': {'car': utils.CAR_FIELDS},
    'limit': 2,
}


@pytest.mark.parametrize(
    'parks_response,expected_code',
    [
        ({'total': 0, 'offset': 0, 'limit': 2, 'cars': []}, 200),
        (
            {
                'total': 2,
                'offset': 0,
                'limit': 2,
                'cars': [{'car_id': '111'}, {'car_id': '222'}],
            },
            200,
        ),
    ],
)
def test_ok(
        taxi_fleet_management_api,
        mockserver,
        dispatcher_access_control,
        parks_response,
        expected_code,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return parks_response

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(LIST_REQUEST),
    )

    assert response.status_code == 200, response.text
    assert response.json() == parks_response

    assert dispatcher_access_control.times_called == 1
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(mock_json_request)
    assert mock_json_request == PARKS_REQUEST


@pytest.mark.parametrize(
    'fields,intersected_fields',
    [
        (None, utils.CAR_FIELDS),
        ({}, utils.CAR_FIELDS),
        ({'abra': ['kadabra']}, utils.CAR_FIELDS),
        ({'car': ['id', 'car_id']}, ['id']),
        ({'car': ['hren`', 'car_id']}, ['id']),
    ],
)
def test_fields_intersection(
        taxi_fleet_management_api, mockserver, fields, intersected_fields,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(mock_request):
        mock_request.get_data()
        return {}

    request_json = {'query': {'park': {'id': 'xxx'}}}
    if fields is not None:
        request_json['fields'] = fields

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_json),
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(mock_json_request)
    assert mock_json_request['fields']['car'] == intersected_fields


def test_bad_request(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS,
    )

    assert mock_callback.times_called == 0
    assert response.status_code == 400, response.text
    assert response.json() == utils.format_error(
        'request must be in json format',
    )


def test_default_offset_limit(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return {'total': 0, 'offset': 0, 'limit': 1000, 'cars': []}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        data=json.dumps({'query': {'park': {'id': 'xxx'}}}),
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(mock_json_request)
    assert 'offset' not in mock_json_request
    assert mock_json_request['limit'] == 1000


def test_is_rental_filter(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        data=json.dumps(
            {
                'query': {
                    'park': {
                        'id': 'rental_cars_park',
                        'car': {'is_rental': True},
                    },
                },
            },
        ),
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    print(mock_json_request)
    assert 'query' in mock_json_request
    assert 'park' in mock_json_request['query']
    assert 'car' in mock_json_request['query']['park']
    assert 'is_rental' in mock_json_request['query']['park']['car']
    assert mock_json_request['query']['park']['car']['is_rental'] is True
