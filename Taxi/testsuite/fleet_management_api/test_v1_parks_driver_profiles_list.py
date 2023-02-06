import json

import pytest

from . import auth
from . import utils

MOCK_URL = '/parks/driver-profiles/list'
ENDPOINT_URL = '/v1/parks/driver-profiles/list'

FIELDS_PARAMS = [  # type: ignore
    (
        None,
        {
            'account': utils.ACCOUNT_FIELDS,
            'car': utils.CAR_FIELDS,
            'driver_profile': utils.DRIVER_PROFILE_FIELDS,
            'park': utils.PARK_FIELDS,
            'current_status': utils.CURRENT_STATUS_FIELDS,
            'deptrans': utils.DEPTRANS_FIELDS,
        },
    ),
    (
        {},
        {
            'account': utils.ACCOUNT_FIELDS,
            'car': utils.CAR_FIELDS,
            'driver_profile': utils.DRIVER_PROFILE_FIELDS,
            'park': utils.PARK_FIELDS,
            'current_status': utils.CURRENT_STATUS_FIELDS,
            'deptrans': utils.DEPTRANS_FIELDS,
        },
    ),
    (
        {'abra': ['kadabra']},
        {
            'account': utils.ACCOUNT_FIELDS,
            'car': utils.CAR_FIELDS,
            'driver_profile': utils.DRIVER_PROFILE_FIELDS,
            'park': utils.PARK_FIELDS,
            'current_status': utils.CURRENT_STATUS_FIELDS,
            'deptrans': utils.DEPTRANS_FIELDS,
        },
    ),
    (
        {'account': []},
        {
            'car': utils.CAR_FIELDS,
            'driver_profile': utils.DRIVER_PROFILE_FIELDS,
            'park': utils.PARK_FIELDS,
            'current_status': utils.CURRENT_STATUS_FIELDS,
            'deptrans': utils.DEPTRANS_FIELDS,
        },
    ),
    (
        {'car': []},
        {
            'account': utils.ACCOUNT_FIELDS,
            'driver_profile': utils.DRIVER_PROFILE_FIELDS,
            'park': utils.PARK_FIELDS,
            'current_status': utils.CURRENT_STATUS_FIELDS,
            'deptrans': utils.DEPTRANS_FIELDS,
        },
    ),
    (
        {'driver_profile': []},
        {
            'account': utils.ACCOUNT_FIELDS,
            'car': utils.CAR_FIELDS,
            'driver_profile': ['id'],
            'park': utils.PARK_FIELDS,
            'current_status': utils.CURRENT_STATUS_FIELDS,
            'deptrans': utils.DEPTRANS_FIELDS,
        },
    ),
    (
        {'park': []},
        {
            'account': utils.ACCOUNT_FIELDS,
            'car': utils.CAR_FIELDS,
            'driver_profile': utils.DRIVER_PROFILE_FIELDS,
            'park': ['id'],
            'current_status': utils.CURRENT_STATUS_FIELDS,
            'deptrans': utils.DEPTRANS_FIELDS,
        },
    ),
    (
        {
            'account': [],
            'car': [],
            'driver_profile': [],
            'park': [],
            'current_status': [],
            'deptrans': [],
        },
        {'driver_profile': ['id'], 'park': ['id']},
    ),
    (
        {
            'account': ['xxl', 'something', 'driver_secret'],
            'car': ['zZ'],
            'driver_profile': ['balance', 'balance_limit', 'xxx'],
            'park': ['abra', 'kadabra'],
            'current_status': [],
            'deptrans': [],
        },
        {
            'account': ['id'],
            'car': ['id'],
            'driver_profile': ['id'],
            'park': ['id'],
        },
    ),
    (
        {
            'account': ['balance', 'type', 'driver_secret'],
            'car': ['normalized_number', 'brand', 'oO'],
            'driver_profile': ['balance', 'first_name', 'license', 'yyy'],
            'park': ['city', 'abra', 'kadabra'],
            'current_status': [],
            'deptrans': [],
        },
        {
            'account': ['balance', 'id', 'type'],
            'car': ['brand', 'id', 'normalized_number'],
            'driver_profile': ['first_name', 'id', 'license'],
            'park': ['city', 'id'],
        },
    ),
    (
        {
            'account': [],
            'car': [],
            'driver_profile': [],
            'park': [],
            'aggregate': {
                'account': [
                    'positive_balance_sum',
                    'negative_balance_sum',
                    'balance_limit_sum',
                ],
            },
            'current_status': [],
            'deptrans': [],
        },
        {
            'driver_profile': ['id'],
            'park': ['id'],
            'aggregate': {
                'account': [
                    'positive_balance_sum',
                    'negative_balance_sum',
                    'balance_limit_sum',
                ],
            },
        },
    ),
    (
        {
            'account': [],
            'car': [],
            'driver_profile': [],
            'park': [],
            'current_status': ['status', 'asdf'],
            'deptrans': [],
        },
        {
            'driver_profile': ['id'],
            'park': ['id'],
            'current_status': ['status'],
        },
    ),
]


@pytest.mark.parametrize(
    'request_fields,expected_parks_request_fields', FIELDS_PARAMS,
)
def test_fields(
        taxi_fleet_management_api,
        mockserver,
        request_fields,
        expected_parks_request_fields,
):
    ok_response = {
        'limit': 1000,
        'offset': 0,
        'total': 0,
        'driver_profiles': [],
        'parks': [{'id': 'park_X'}],
    }

    json_request = {'query': {'park': {'id': 'park_X'}}}

    expected_mock_json_request = {
        'query': {'park': {'id': 'park_X'}},
        'fields': expected_parks_request_fields,
        'limit': 1000,
        'removed_drivers_mode': 'hide_all_fields',
    }

    if request_fields:
        json_request['fields'] = request_fields

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return ok_response

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, data=json.dumps(json_request),
    )

    assert response.status_code == 200, response.text
    assert response.json() == ok_response
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    utils.check_query_park_car_categories_filter(mock_json_request)
    assert mock_json_request == expected_mock_json_request


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
def test_query_proxy(taxi_fleet_management_api, mockserver, query):
    ok_response = {
        'limit': 1000,
        'offset': 0,
        'total': 0,
        'driver_profiles': [],
        'parks': [{'id': 'park_X'}],
    }

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return ok_response

    response = taxi_fleet_management_api.post(
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


@pytest.mark.parametrize(
    'request_json,error_text',
    [
        ({}, 'query must be present'),
        ({'query': {}}, 'query.park must be present'),
        ({'query': {'park': {}}}, 'query.park.id must be present'),
        (
            {'query': {'park': {'id': ''}}},
            'query.park.id must be a non-empty utf-8 string without BOM',
        ),
        (
            {
                'query': {'park': {'id': 'park_Zz'}},
                'fields': {'park': ['city', 'city']},
            },
            'fields.park must contain unique strings (error at `city`)',
        ),
        (
            {
                'query': {'park': {'id': 'park_Zz'}},
                'fields': {'driver_profile': ['last_name', 'id', 'id']},
            },
            'fields.driver_profile must contain '
            'unique strings (error at `id`)',
        ),
        (
            {
                'query': {'park': {'id': 'park_Zz'}},
                'fields': {
                    'account': ['type', 'balance', 'currency', 'balance'],
                },
            },
            'fields.account must contain unique strings (error at `balance`)',
        ),
        (
            {'query': {'park': {'id': 'park_Zz'}}, 'limit': 1001},
            'limit must be less than or equal to 1000',
        ),
    ],
)
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
        data=json.dumps({'query': {'park': {'id': 'xxx'}}}),
    )

    assert mock_callback.times_called == 1
    assert response.status_code == status_code
    assert response.json() == expected_response


def test_default_offset_limit(taxi_fleet_management_api, mockserver):
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

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        headers=auth.HEADERS,
        data=json.dumps({'query': {'park': {'id': 'park_X'}}}),
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    assert 'offset' not in mock_json_request
    assert mock_json_request['limit'] == 1000


def test_do_not_remove_current_status(taxi_fleet_management_api, mockserver):
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

    response = taxi_fleet_management_api.post(
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
    assert mock_json_request['query']['park']['current_status']['status'] == [
        'busy',
    ], mock_json_request
