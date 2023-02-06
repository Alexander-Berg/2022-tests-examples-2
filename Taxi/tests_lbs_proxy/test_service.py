import json

import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from lbs_cloud_proxy_plugins.generated_tests import *  # noqa


async def test_adding_key(taxi_lbs_cloud_proxy, mockserver):
    @mockserver.json_handler('/geolocation')
    def _geolocation_handler(request):
        assert request.get_data()[:5] == b'json='
        body = json.loads(request.get_data()[5:])
        if body['common']['api_key'] == '1234':
            del body['common']
            return body
        return {'fail': 'fail'}

    params = {'hello': 'param'}
    response = await taxi_lbs_cloud_proxy.post('lbs', json=params)
    assert response.status_code == 200
    assert response.json()['hello'] == params['hello']


@pytest.mark.parametrize(
    'mock_path,server_path',
    [('/geolocation', 'lbs'), ('/geolocation_batch', 'lbs_batch')],
)
async def test_pass_headers(
        taxi_lbs_cloud_proxy, mockserver, mock_path, server_path,
):
    @mockserver.json_handler(mock_path)
    def _geolocation_handler(request):
        assert request.query == {'device_id': 'some', 'uuid': 'any'}
        return {'hello': 'param'}

    params = {'hello': 'param'}
    query_params = {'device_id': 'some', 'uuid': 'any'}
    response = await taxi_lbs_cloud_proxy.post(
        server_path, json=params, params=query_params,
    )
    assert response.status_code == 200
    assert response.json()['hello'] == params['hello']


async def test_adding_key_batch(taxi_lbs_cloud_proxy, mockserver):
    @mockserver.json_handler('/geolocation_batch')
    def _geolocation_handler(request):
        body = json.loads(request.get_data())
        if body['common']['api_key'] == '1234':
            del body['common']
            return body
        return {'fail': 'fail'}

    params = {'hello': 'param'}
    response = await taxi_lbs_cloud_proxy.post('lbs_batch', json=params)
    assert response.status_code == 200
    assert response.json()['hello'] == params['hello']


@pytest.mark.parametrize(
    ('message', 'code', 'status', 'response_code'),
    [
        (
            # return 500 on incorrect api key
            {},
            403,
            500,
            500,
        ),
        (
            # return 200 and message on 400
            {'error': {'message': 'Malformed', 'code': 10}},
            400,
            200,
            10,
        ),
        (
            # return 500 and 500 code on 500
            {},
            500,
            500,
            500,
        ),
        (
            # return 200 and message on 404 (not found)
            {'error': {'message': 'Location not found', 'code': 6}},
            404,
            200,
            6,
        ),
    ],
)
async def test_lbs_api_errors(
        taxi_lbs_cloud_proxy, message, code, status, response_code, mockserver,
):
    @mockserver.handler('/geolocation')
    def _geolocation_handler(request):
        return mockserver.make_response(json.dumps(message), code)

    response = await taxi_lbs_cloud_proxy.post('lbs', json={})
    assert response.status_code == status
    body = response.json()
    assert body['error']['code'] == response_code


async def test_x_yarequest_id(taxi_lbs_cloud_proxy, mockserver):
    @mockserver.handler('/geolocation')
    def _geolocation_handler(request):
        return mockserver.make_response(
            '{}', headers={'X-YaRequestId': '12345'}, status=200,
        )

    response = await taxi_lbs_cloud_proxy.post('lbs', json={})
    assert response.status_code == 200
    assert response.headers['X-LBS-YaRequestId'] == '12345'
