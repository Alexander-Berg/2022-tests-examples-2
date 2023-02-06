import json

import pytest

from . import auth
from . import utils

MOCK_URL = '/parks/driver-profiles/retrieve'
ENDPOINT_URL = '/v1/parks/driver-profiles/retrieve'

OK_PARAMS = [
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'account': utils.ACCOUNT_FIELDS},
        }
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'car': utils.CAR_FIELDS},
        }
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'driver_profile': utils.DRIVER_PROFILE_FIELDS},
        }
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {
                'taximeter_disable_status': (
                    utils.TAXIMETER_DISABLE_STATUS_FIELDS
                ),
            },
        }
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {
                'account': utils.ACCOUNT_FIELDS,
                'car': utils.CAR_FIELDS,
                'driver_profile': utils.DRIVER_PROFILE_FIELDS,
            },
        }
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'current_status': utils.CURRENT_STATUS_FIELDS},
        }
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'rating': utils.RATING_FIELDS},
        }
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'driver_metrics': utils.DRIVER_METRICS_FIELDS},
        }
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'child_chairs': ['some_field']},
        }
    ),
]


@pytest.mark.parametrize('request_json', OK_PARAMS)
def test_ok(taxi_fleet_management_api, mockserver, request_json):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_json),
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(mock_json_request)
    assert mock_json_request == request_json


def test_set_config(taxi_fleet_management_api, mockserver, config):
    REQUEST_JSON = {
        'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
        'fields': {'account': utils.ACCOUNT_FIELDS},
    }
    CATEGORIES = ['econom', 'comfort']

    config.set_values(
        dict(
            FLEET_API_CAR_CATEGORIES={
                'internal_categories': CATEGORIES,
                'external_categories': [],
            },
        ),
    )

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(REQUEST_JSON),
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(
        mock_json_request, categories=CATEGORIES,
    )
    assert mock_json_request == REQUEST_JSON


BAD_REQUEST_PARAMS = [
    ({}, 'query must be present'),
    ({'query': {}}, 'query.park must be present'),
    ({'query': {'park': {}}}, 'query.park.id must be present'),
    (
        {'query': {'park': {'id': ''}}},
        'query.park.id must be a non-empty utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': 'x'}}},
        'query.park.driver_profile must be present',
    ),
    (
        {'query': {'park': {'id': 'x', 'driver_profile': {}}}},
        'query.park.driver_profile.id must be present',
    ),
    (
        {'query': {'park': {'id': 'x', 'driver_profile': {'id': ''}}}},
        'query.park.driver_profile.id '
        'must be a non-empty utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}}},
        'fields must be present',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'account': ['a', 'balance', 'c', 'balance']},
        },
        'fields.account must contain unique strings (error at `balance`)',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'car': ['qqq', 'vvv', 'qqq']},
        },
        'fields.car must contain unique strings (error at `qqq`)',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'driver_profile': ['imei', 'car_id', 'imei']},
        },
        'fields.driver_profile must contain unique strings (error at `imei`)',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'account': [], 'driver_profile': []},
        },
        'fields must contain at least one field',
    ),
]


@pytest.mark.parametrize('request_json,error_text', BAD_REQUEST_PARAMS)
def test_bad_request(taxi_fleet_management_api, request_json, error_text):
    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(request_json),
    )

    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)


@pytest.mark.parametrize(
    'status_code,response_text,expected_response',
    [
        (
            400,
            json.dumps({'error': {'text': 'invalid'}}),
            utils.format_error('invalid'),
        ),
        (403, 'something', utils.UNKNOWN_ERROR),
        (500, 'unknown', utils.INTERNAL_ERROR),
    ],
)
def test_parks_not_ok(
        taxi_fleet_management_api,
        mockserver,
        status_code,
        response_text,
        expected_response,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(response_text, status_code)

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        data=json.dumps(
            {
                'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
                'fields': {'driver_profile': ['id']},
            },
        ),
    )

    assert mock_callback.times_called == 1
    assert response.status_code == status_code
    assert response.json() == expected_response
