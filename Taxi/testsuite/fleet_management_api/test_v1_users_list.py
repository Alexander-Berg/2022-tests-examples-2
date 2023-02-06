import json

import pytest
import werkzeug

from . import auth
from . import utils

MOCK_URL = '/dispatcher-access-control/v1/parks/users/list'
ENDPOINT_URL = '/v1/users/list'


def make_request(is_before_fleet, limit=None, offset=None):
    result = {'query': {'park': {'id': 'park1'}}}
    if not is_before_fleet:
        if limit is None:
            result['limit'] = 100
    if limit is not None:
        result['limit'] = limit
    if offset is not None:
        result['offset'] = offset
    return result


def make_response_from_dispatcher(limit=None, offset=None):
    result = {
        'users': [
            {
                'id': 'user1',
                'park_id': 'park1',
                'passport_uid': '1',
                'is_enabled': True,
                'is_superuser': False,
                'is_confirmed': False,
                'is_usage_consent_accepted': False,
            },
        ],
        'limit': limit if limit is not None else 100,
        'offset': offset if offset is not None else 0,
    }
    return result


@pytest.mark.parametrize(
    'limit, offset', [(None, None), (None, 0), (1, None), (1, 0), (42, 43)],
)
def test_ok(taxi_fleet_management_api, mockserver, limit, offset):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return make_response_from_dispatcher(limit, offset)

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        json=make_request(True, limit, offset),
        headers=auth.HEADERS,
    )

    assert response.status_code == 200
    assert mock_callback.times_called == 1
    assert response.json() == make_response_from_dispatcher(limit, offset)

    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    mock_json_request = json.loads(mock_request.get_data())
    assert mock_json_request == make_request(False, limit, offset)


@pytest.mark.parametrize(
    'limit, error_message',
    [
        (0, 'limit must be greater than or equal to 1'),
        (101, 'limit must be less than or equal to 100'),
    ],
)
def test_invalid_limit(
        taxi_fleet_management_api, mockserver, limit, error_message,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, json=make_request(True, limit), headers=auth.HEADERS,
    )
    assert response.status_code == 400
    assert mock_callback.times_called == 0
    assert response.json() == utils.format_error(error_message)


@pytest.mark.parametrize(
    'query_park_id, query_park_id_value, error_message',
    [
        ('wrong_key', 'park1', 'query.park.id must be present'),
        (
            'id',
            12,
            'query.park.id must be a non-empty utf-8 string without BOM',
        ),
        (
            'id',
            ['park1', 'park2'],
            'query.park.id must be a non-empty utf-8 string without BOM',
        ),
        (
            'id',
            '',
            'query.park.id must be a non-empty utf-8 string without BOM',
        ),
    ],
)
def test_invalid_park_id(
        taxi_fleet_management_api,
        mockserver,
        query_park_id,
        query_park_id_value,
        error_message,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL,
        json={'query': {'park': {query_park_id: query_park_id_value}}},
        headers=auth.HEADERS,
    )
    assert response.status_code == 400
    assert mock_callback.times_called == 0
    assert response.json() == utils.format_error(error_message)


def test_dispatcher_access_control_400(taxi_fleet_management_api, mockserver):
    error_message = 'some_message'

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return werkzeug.Response(
            json.dumps({'message': error_message, 'code': '400'}), 400,
        )

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, json=make_request(True), headers=auth.HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'some_message'}
    assert mock_callback.times_called == 1
