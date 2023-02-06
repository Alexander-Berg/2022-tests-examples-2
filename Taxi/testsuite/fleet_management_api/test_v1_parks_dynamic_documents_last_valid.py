import json

import pytest

from . import auth
from . import utils


ENDPOINT_URL = 'v1/parks/dynamic-documents/last-valid'
MOCK_URL = '/document_templator/v1/dynamic_documents/last_valid'
OK_PARAMS = {'park_id': 'some-park-id', 'id': 'some-document-id'}


BAD_REQUEST_PARAMS = [
    ({}, 'parameter park_id must be set'),
    ({'id': 'some-id'}, 'parameter park_id must be set'),
    ({'park_id': 'some-park-id'}, 'parameter id must be set'),
]


@pytest.mark.parametrize('params, error_text', BAD_REQUEST_PARAMS)
def test_bad_request(
        taxi_fleet_management_api, mockserver, params, error_text,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, headers=auth.HEADERS, params=params,
    )

    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)
    assert mock_callback.times_called == 0


def test_ok(taxi_fleet_management_api, mockserver):
    ok_response = {'id': 'some-document-id', 'name': 'имя', 'text': 'текст'}

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return ok_response

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, headers=auth.HEADERS, params=OK_PARAMS,
    )

    assert response.status_code == 200, response.text
    assert response.json() == ok_response, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'GET'
    assert mock_request.args.to_dict() == {'id': 'some-document-id'}


CLIENT_ERROR_PARAMS = [(400, 'invalid id'), (404, 'id not found')]


@pytest.mark.parametrize('code, message', CLIENT_ERROR_PARAMS)
def test_client_error(taxi_fleet_management_api, mockserver, code, message):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(
            json.dumps({'code': str(code), 'message': message}), code,
        )

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, headers=auth.HEADERS, params=OK_PARAMS,
    )

    assert response.status_code == code, response.text
    assert response.json() == utils.format_error(message, code)
    assert mock_callback.times_called == 1


@pytest.mark.parametrize('code', [401, 403, 500])
def test_internal_error(taxi_fleet_management_api, mockserver, code):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(
            json.dumps({'code': str(code), 'message': 'err'}), code,
        )

    response = taxi_fleet_management_api.get(
        ENDPOINT_URL, headers=auth.HEADERS, params=OK_PARAMS,
    )

    assert response.status_code == 500, response.text
    assert response.json() == utils.INTERNAL_ERROR
    assert mock_callback.times_called == 1
