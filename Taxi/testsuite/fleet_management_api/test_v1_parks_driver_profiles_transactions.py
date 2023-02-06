import json

import pytest

from . import auth
from . import utils

MOCK_BASE_URL = (
    '/taximeter-xservice.taxi.yandex.net/fm-api/driver/transactions'
)
ENDPOINT_BASE_URL = '/v1/parks/driver-profiles/transactions'


def test_get(taxi_fleet_management_api, mockserver):
    @mockserver.json_handler(MOCK_BASE_URL)
    def mock_callback(request):
        assert request.args.to_dict() == {
            'park_id': 'abab',
            'transaction_id': 'DADA1212',
        }
        utils.check_headers(request.headers, utils.X_REAL_IP_HEADERS)
        return {'status': 'pending'}

    response = taxi_fleet_management_api.get(
        ENDPOINT_BASE_URL,
        headers=auth.HEADERS,
        params={'park_id': 'abab', 'transaction_id': 'DADA1212'},
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'pending'}


@pytest.mark.parametrize(
    'params,error_text',
    [
        ({}, 'parameter park_id must be set'),
        (
            {'park_id': 'strange\r\nthings'},
            'parameter park_id data is invalid',
        ),
        ({'park_id': 'baab1243'}, 'parameter transaction_id must be set'),
        (
            {'park_id': 'baab1243', 'transaction_id': 'what\ris\ngoind\ton'},
            'parameter transaction_id data is invalid',
        ),
    ],
)
def test_get_bad_request(taxi_fleet_management_api, params, error_text):
    response = taxi_fleet_management_api.get(
        ENDPOINT_BASE_URL, headers=auth.HEADERS, params=params,
    )

    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)


def test_post(taxi_fleet_management_api, mockserver):
    request_body = {'park_id': 'xXx', 'any_field': 'any_value'}

    @mockserver.json_handler(MOCK_BASE_URL)
    def mock_callback(request):
        assert request.args.to_dict() == {}
        request_body_copy = request_body.copy()
        request_body_copy.update({'service_id': auth.OPTEUM_SERVICE_ID})
        assert json.loads(request.get_data()) == request_body_copy
        utils.check_headers(request.headers, utils.X_REAL_IP_HEADERS)
        return {'status': 'draft'}

    request_body_copy = request_body.copy()
    request_body_copy.update({'service_id': 'abrakadabra'})
    response = taxi_fleet_management_api.post(
        ENDPOINT_BASE_URL,
        headers=auth.HEADERS,
        data=json.dumps(request_body_copy),
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'draft'}


def test_commit(taxi_fleet_management_api, mockserver):
    json_data = {'park_id': 'baab', 'transaction_id': 'FEFE3434'}

    ok_response = {'status': 'success'}

    @mockserver.json_handler(MOCK_BASE_URL + '/commit')
    def mock_callback(request):
        assert request.args.to_dict() == {}
        assert json.loads(request.get_data()) == json_data
        utils.check_headers(request.headers, utils.X_REAL_IP_HEADERS)
        return ok_response

    response = taxi_fleet_management_api.post(
        ENDPOINT_BASE_URL + '/commit',
        headers=auth.HEADERS,
        data=json.dumps(json_data),
    )

    assert response.status_code == 200
    assert response.json() == ok_response


@pytest.mark.parametrize(
    'query,internal_query',
    [
        (
            {
                'query': {
                    'park': {'id': 'abcdef54321'},
                    'driver': {'ids': ['ac', 'bc']},
                    'document': {'field': 'value'},
                },
                'limit': 1000,
            },
            {
                'query': {
                    'park': {'id': 'abcdef54321'},
                    'driver': {'ids': ['ac', 'bc']},
                    'document': {'field': 'value'},
                },
                'limit': 1000,
            },
        ),
    ],
)
def test_list(taxi_fleet_management_api, query, internal_query, mockserver):
    ok_response = {'transactions': []}

    @mockserver.json_handler(MOCK_BASE_URL + '/list')
    def mock_callback(request):
        assert request.args.to_dict() == {}
        assert json.loads(request.get_data()) == internal_query
        utils.check_headers(request.headers, utils.X_REAL_IP_HEADERS)
        return ok_response

    response = taxi_fleet_management_api.post(
        ENDPOINT_BASE_URL + '/list',
        headers=auth.HEADERS,
        data=json.dumps(query),
    )

    assert response.status_code == 200
    assert response.json() == ok_response


@pytest.mark.parametrize(
    'query,error_text',
    [
        (123, 'json root must be an object'),
        (
            {'query': {'document': {'field': 'value'}}},
            'query.park must be present',
        ),
        (
            {'query': {'park': {}, 'document': {'field': 'value'}}},
            'query.park.id must be present',
        ),
        (
            {'query': {'park': {'id': ''}, 'document': {'field': 'value'}}},
            'query.park.id must be a non-empty utf-8 string without BOM',
        ),
    ],
)
def test_list_bad_request(taxi_fleet_management_api, query, error_text):
    response = taxi_fleet_management_api.post(
        ENDPOINT_BASE_URL + '/list',
        headers=auth.HEADERS,
        data=json.dumps(query),
    )

    assert response.status_code == 400
    assert response.json() == utils.format_error(error_text)


@pytest.mark.parametrize(
    'status_code,response_text,expected_response',
    [
        (
            400,
            json.dumps({'message': 'bad message'}),
            utils.format_error('bad message'),
        ),
        (
            400,
            json.dumps(
                {'message': 'invalid arguments', 'code': 'invalid_arguments'},
            ),
            utils.format_error('invalid arguments', 'invalid_arguments'),
        ),
        (400, json.dumps({'code': 'unknown code'}), utils.UNKNOWN_ERROR),
        (403, 'some body', utils.UNKNOWN_ERROR),
        (500, 'unknown body', utils.INTERNAL_ERROR),
    ],
)
def test_transactions_not_ok(
        taxi_fleet_management_api,
        mockserver,
        status_code,
        response_text,
        expected_response,
):
    @mockserver.json_handler(MOCK_BASE_URL)
    def mock_callback(request):
        return mockserver.make_response(response_text, status_code)

    response = taxi_fleet_management_api.get(
        ENDPOINT_BASE_URL,
        headers=auth.HEADERS,
        params={'park_id': 'cae1', 'transaction_id': 'feba3'},
    )

    assert response.status_code == status_code
    if expected_response:
        assert response.json() == expected_response


def test_transactions_groups_ok(taxi_fleet_management_api, mockserver):
    taximeter_response = [{'id': 'string', 'name': 'string'}]

    @mockserver.json_handler(MOCK_BASE_URL + '/groups')
    def mock_callback(request):
        return taximeter_response

    response = taxi_fleet_management_api.get(
        ENDPOINT_BASE_URL + '/groups',
        headers=auth.HEADERS,
        params={'park_id': 'baab'},
    )

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.args.to_dict() == {'park_id': 'baab'}
    assert mock_request.get_data() == b''
    utils.check_headers(mock_request.headers, utils.X_REAL_IP_HEADERS)

    assert response.status_code == 200, response.text
    assert response.json() == taximeter_response


@pytest.mark.parametrize(
    'params, status_code, expected_response',
    [
        ({}, 400, utils.format_error('parameter park_id must be set')),
        (
            {'park_id': 'b\n'},
            400,
            utils.format_error('parameter park_id data is invalid'),
        ),
    ],
)
def test_transactions_groups_not_ok(
        taxi_fleet_management_api,
        mockserver,
        params,
        status_code,
        expected_response,
):
    @mockserver.json_handler(MOCK_BASE_URL + '/groups')
    def mock_callback(request):
        return {}

    response = taxi_fleet_management_api.get(
        ENDPOINT_BASE_URL + '/groups', headers=auth.HEADERS, params=params,
    )
    assert mock_callback.times_called == 0
    assert response.status_code == status_code, response.text
    assert response.json() == expected_response
