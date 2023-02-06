import json

import pytest

from fleet_management_api import utils
from . import auth


MOCK_URL = '/parks/driver-profiles/list'
ENDPOINT_URL = '/v1/parks/driver-profiles/list'
PARK_ID = 'park_X'


@pytest.mark.parametrize(
    'request_fields,expected_parks_request_fields',
    [
        (
            None,
            {
                'account': utils.ACCOUNT_FIELDS,
                'car': utils.EXTERNAL_CAR_FIELDS,
                'current_status': utils.EXTERNAL_CURRENT_STATUS_FIELDS,
                'driver_profile': utils.EXTERNAL_DRIVER_PROFILE_FIELDS,
                'park': utils.EXTERNAL_PARK_FIELDS,
            },
        ),
        (
            {
                'account': utils.ACCOUNT_FIELDS,
                'car': utils.CAR_FIELDS,
                'driver_profile': utils.DRIVER_PROFILE_FIELDS,
                'park': utils.PARK_FIELDS,
            },
            {
                'account': utils.EXTERNAL_ACCOUNT_FIELDS,
                'car': utils.EXTERNAL_CAR_FIELDS,
                'driver_profile': utils.EXTERNAL_DRIVER_PROFILE_FIELDS,
                'current_status': utils.EXTERNAL_CURRENT_STATUS_FIELDS,
                'park': utils.EXTERNAL_PARK_FIELDS,
            },
        ),
    ],
)
def test_ok(
        taxi_fleet_api_external,
        mockserver,
        request_fields,
        expected_parks_request_fields,
):
    ok_response = {
        'offset': 0,
        'total': 0,
        'driver_profiles': [],
        'parks': [{'id': PARK_ID}],
    }

    json_request = {'query': {'park': {'id': PARK_ID}}}

    if request_fields:
        json_request['fields'] = request_fields

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return ok_response

    response = taxi_fleet_api_external.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(json_request),
    )

    assert response.status_code == 200, response.text
    assert response.json() == ok_response

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(mock_json_request)
    assert mock_json_request == {
        'query': {'park': {'id': PARK_ID}},
        'fields': expected_parks_request_fields,
        'limit': 1000,
        'removed_drivers_mode': 'hide_all_fields',
    }


PROXY_REQUEST_PARAMS = [
    {
        'park': {
            'id': 'park_X',
            'account': {
                'last_transaction_date': {
                    'from': '2016-01-01T10:00:00+0000',
                    'to': '2017-01-01T10:00:00+0000',
                },
            },
        },
    },
]


@pytest.mark.parametrize('query', PROXY_REQUEST_PARAMS)
def test_query_proxy(taxi_fleet_api_external, mockserver, query):
    ok_response = {
        'limit': 100,
        'offset': 0,
        'total': 0,
        'driver_profiles': [],
        'parks': [{'id': 'park_X'}],
    }

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return ok_response

    response = taxi_fleet_api_external.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        data=json.dumps(
            {
                'query': query,
                'fields': {'park': ['id'], 'driver_profile': ['id']},
                'limit': 1000,
            },
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json() == ok_response
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    # car filter is checked in previous test
    mock_json_request['query']['park'].pop('car')
    assert mock_json_request['query'] == query


def test_remove_current_status(taxi_fleet_api_external, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return {
            'total': 0,
            'offset': 0,
            'limit': 1000,
            'driver_profiles': [],
            'parks': [],
        }

    response = taxi_fleet_api_external.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        data=json.dumps(
            {
                'query': {
                    'park': {
                        'id': 'park_X',
                        'current_status': {'status': ['busy']},
                    },
                },
            },
        ),
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    mock_json_request = json.loads(mock_request.get_data())
    assert 'current_status' not in mock_json_request['query']['park']
