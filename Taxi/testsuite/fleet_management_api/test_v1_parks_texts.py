import json

import pytest

from . import auth
from . import utils

MOCK_URL = '/parks/texts'
ENDPOINT_URL = '/v1/parks/texts'


@pytest.mark.parametrize(
    'park_id,text_type,expected_status_code,expected_message',
    [
        ('', 'terms', 400, 'parameter park_id must be set'),
        ('777', '', 400, 'parameter text_type must be set'),
    ],
)
def test_invalid_args(
        taxi_fleet_management_api,
        mockserver,
        park_id,
        text_type,
        expected_status_code,
        expected_message,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL,
        params={'park_id': park_id, 'text_type': text_type},
        headers=auth.HEADERS,
    )

    assert mock_callback.times_called == 0
    assert response.status_code == expected_status_code, response.text
    assert response.json() == utils.format_error(expected_message)


@pytest.mark.parametrize(
    'parks_response_json,response_json,response_code',
    [
        ({'text': 'text body'}, {'text': 'text body'}, 200),
        (
            {'error': {'text': 'invalid args'}},
            utils.format_error('invalid args'),
            400,
        ),
        (
            {'error': {'text': 'invalid args', 'code': 'invalid_args'}},
            utils.format_error('invalid args', 'invalid_args'),
            400,
        ),
        ({'message': 'text not found'}, utils.UNKNOWN_ERROR, 404),
        ({'message': '', 'code': 'some_error'}, utils.UNKNOWN_ERROR, 404),
    ],
)
def test_authorized_parks_proxy(
        taxi_fleet_management_api,
        mockserver,
        parks_response_json,
        response_json,
        response_code,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(
            json.dumps(parks_response_json), response_code,
        )

    query = {'park_id': 'id', 'text_type': 'type'}

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, params=query, headers=auth.HEADERS,
    )

    assert mock_callback.times_called == 1
    parks_request = mock_callback.next_call()['request']
    assert parks_request.method == 'GET'
    assert parks_request.args.to_dict() == query

    assert response.status_code == response_code
    assert response.json() == response_json
