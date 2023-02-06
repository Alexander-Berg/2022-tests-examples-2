import json

import pytest

from . import auth
from . import utils


ENDPOINT_URL_PREFIX = 'v2/'
ENDPOINT_URLS = [
    'parks/transactions/list',
    'parks/driver-profiles/transactions/list',
    'parks/orders/transactions/list',
]

MOCK_BASE_URL = '/fleet_transactions_api/v1/'


BAD_REQUEST_PARAMS = [
    (123, 'json root must be an object'),
    ({'query': {}}, 'query.park must be present'),
    ({'query': {'park': {}}}, 'query.park.id must be present'),
    (
        {'query': {'park': {'id': ''}}},
        'query.park.id must be a non-empty utf-8 string without BOM',
    ),
]


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize('query,error_text', BAD_REQUEST_PARAMS)
def test_bad_request(
        taxi_fleet_management_api, mockserver, endpoint_url, query, error_text,
):
    @mockserver.json_handler(MOCK_BASE_URL + endpoint_url)
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL_PREFIX + endpoint_url,
        headers=auth.HEADERS,
        data=json.dumps(query),
    )

    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)
    assert mock_callback.times_called == 0


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_ok(taxi_fleet_management_api, mockserver, load_json, endpoint_url):
    ok_request = load_json('ok_request.json')
    ok_response = load_json('ok_response.json')

    @mockserver.json_handler(MOCK_BASE_URL + endpoint_url)
    def mock_callback(request):
        request.get_data()
        return ok_response

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL_PREFIX + endpoint_url,
        headers=auth.HEADERS,
        data=json.dumps(ok_request),
    )

    assert response.status_code == 200, response.text
    assert response.json() == ok_response, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == ok_request


MOCK_ERROR_PARAMS = [
    (
        400,
        json.dumps({'code': '400', 'message': 'bad message'}),
        utils.format_error('bad message', '400'),
    ),
    (
        400,
        json.dumps({'code': 'some-code', 'message': 'bad message'}),
        utils.format_error('bad message', 'some-code'),
    ),
    (400, 'not a json', utils.format_error('not a json')),
    (
        500,
        json.dumps({'code': '500', 'message': 'internal error'}),
        utils.INTERNAL_ERROR,
    ),
    (500, 'not a json', utils.INTERNAL_ERROR),
]


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'status_code,mock_response_data,response_json', MOCK_ERROR_PARAMS,
)
def test_mock_error(
        taxi_fleet_management_api,
        mockserver,
        load_json,
        endpoint_url,
        status_code,
        mock_response_data,
        response_json,
):
    ok_request = load_json('ok_request.json')

    @mockserver.json_handler(MOCK_BASE_URL + endpoint_url)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(mock_response_data, status_code)

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL_PREFIX + endpoint_url,
        headers=auth.HEADERS,
        data=json.dumps(ok_request),
    )

    assert response.status_code == status_code, response.text
    assert response.json() == response_json, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == ok_request
