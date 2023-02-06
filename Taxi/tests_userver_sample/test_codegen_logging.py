import json

import pytest

DEFAULT_ERROR_CONTENT_TYPE = 'application/json; charset=utf-8'


@pytest.mark.parametrize(
    'url',
    ['autogen/logging/test', 'autogen/logging/test3'],
    ids=['old', 'new'],
)
async def test_logging_ok_request(taxi_userver_sample, url):
    response = await taxi_userver_sample.post(
        url,
        data=json.dumps(
            {'key': 'VALID_JSON_REQUEST and some long long long string'},
        ),
    )
    assert response.status_code == 200
    assert (
        response.headers['Content-Type'] == 'application/json; charset=utf-8'
    )

    response = await taxi_userver_sample.post(
        url, data=json.dumps({'key': 'VALIDATE_RESPONSE_LOGGER_WAS_CALLED'}),
    )
    assert response.status_code == 200, response.text
    assert (
        response.headers['Content-Type'] == 'application/json; charset=utf-8'
    )


@pytest.mark.parametrize(
    'url',
    ['autogen/logging/test', 'autogen/logging/test3'],
    ids=['old', 'new'],
)
async def test_logging_bad_schema_request(taxi_userver_sample, url):
    response = await taxi_userver_sample.post(
        url,
        data=json.dumps(
            {'other_key': 'JSON_REQUEST_SCHEMA_MISSMATCH and some string'},
        ),
    )
    assert response.status_code == 400
    assert 'message' in response.json()
    assert 'code' in response.json()
    assert '\'key\'' in response.json()['message']
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


@pytest.mark.parametrize(
    'url',
    ['autogen/logging/test', 'autogen/logging/test3'],
    ids=['old', 'new'],
)
async def test_logging_non_json_request(taxi_userver_sample, url):
    response = await taxi_userver_sample.post(
        url,
        data='NOT_A_JSON_REQUEST and some long long long long long string',
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


async def test_json_logging_without_json_value(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/logging/test2', data=json.dumps({'key': 'value'}),
    )
    assert response.status_code == 200
    assert (
        response.headers['Content-Type'] == 'application/json; charset=utf-8'
    )


async def test_logging_without_json_value_bad_schema_request(
        taxi_userver_sample,
):
    response = await taxi_userver_sample.post(
        'autogen/logging/test2',
        data=json.dumps(
            {'other_key': 'JSON_REQUEST_SCHEMA_MISSMATCH and some string'},
        ),
    )
    assert response.status_code == 400
    # Message from SAX parser, DOM parser is not used
    assert response.json() == {
        'code': '400',
        'message': (
            'Parse error at pos 61, path \'\': missing required field \'key\''
        ),
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE
