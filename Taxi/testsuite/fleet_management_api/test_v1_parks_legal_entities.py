import json

import pytest

from . import auth
from . import utils

MOCK_URL = '/parks/legal-entities'
ENDPOINT_URL = '/v1/parks/legal-entities'

POST_PARAMS = {'park_id': 'park'}
PARAMS = {'park_id': 'park', 'id': 'legal_entity'}
REQUEST = json.dumps({'some': 'request'})
RESPONSE = {'some': 'response'}
REPEAT_COUNT = 3


@pytest.mark.parametrize('rate_limit', [None, 2, 3])
@pytest.mark.parametrize(
    'method_str, params, body, expected_response',
    [
        ('post', POST_PARAMS, REQUEST, RESPONSE),
        ('put', PARAMS, REQUEST, RESPONSE),
        ('get', PARAMS, '', RESPONSE),
    ],
)
def test(
        taxi_fleet_management_api,
        mockserver,
        config,
        rate_limit,
        method_str,
        params,
        body,
        expected_response,
):
    config.set_values(dict(FLEET_API_LEGAL_ENTITIES_RPH=rate_limit))

    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        request.get_data(cache=True)  # call get_data to save body in request
        return expected_response

    method = {
        'post': taxi_fleet_management_api.post,
        'put': taxi_fleet_management_api.put,
        'get': taxi_fleet_management_api.get,
    }

    for i in range(REPEAT_COUNT):
        response = method[method_str](
            ENDPOINT_URL, headers=auth.HEADERS, params=params, data=body,
        )

        if rate_limit is None or method_str == 'get' or i < rate_limit:
            assert (
                response.status_code == 200
            ), 'itaration {}, response {}'.format(i, response.text)
            assert mock_callback.times_called == 1
            mock_request = mock_callback.next_call()['request']
            assert mock_request.args.to_dict() == params
            assert mock_request.get_data().decode() == body
            assert response.json() == expected_response
        else:
            assert (
                response.status_code == 429
            ), 'itaration {}, response {}'.format(i, response.text)


@pytest.mark.config(FLEET_API_LEGAL_ENTITIES_RPH=None)
@pytest.mark.parametrize(
    'parks_error,expected_error',
    [
        ({'error': {'text': 'some error'}}, utils.format_error('some error')),
        (
            {'error': {'text': 'some text', 'code': 'some code'}},
            utils.format_error('some text', 'some code'),
        ),
    ],
)
def test_error_pass(
        taxi_fleet_management_api, parks_error, expected_error, mockserver,
):
    @mockserver.json_handler(MOCK_URL)
    def mock_callback(request):
        return mockserver.make_response(json.dumps(parks_error), 400)

    response = taxi_fleet_management_api.post(
        ENDPOINT_URL, headers=auth.HEADERS, params=POST_PARAMS, data={},
    )

    assert response.status_code == 400, response.text
    assert mock_callback.times_called == 1
    assert response.json() == expected_error
