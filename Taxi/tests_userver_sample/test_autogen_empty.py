import json

DEFAULT_ERROR_CONTENT_TYPE = 'application/json; charset=utf-8'


async def test_empty_get(taxi_userver_sample):
    response = await taxi_userver_sample.get('autogen/empty')
    assert response.status_code == 200
    assert response.json() == {}


async def test_single_nonjson_response(taxi_userver_sample):
    response = await taxi_userver_sample.delete('autogen/empty')
    assert response.status_code == 200
    assert response.text == 'string'
    assert response.headers['Content-Type'] == 'application/json'


async def test_custom_error_response(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/empty', data=json.dumps({'field1': 'throw'}),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'USER_NOT_FOUND',
        'message': 'some message',
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


async def test_custom_error_details(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/empty', data=json.dumps({'field1': 'throw_details'}),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'USER_NOT_FOUND',
        'message': 'some message',
        'details': {'extra1': 'foo', 'extra2': 'bar'},
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


async def test_custom_throw_client_error(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/empty', data=json.dumps({'field1': 'throw_client_error'}),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'USER_NOT_FOUND',
        'message': 'some other message',
        'details': {'extra1': 'client extra1', 'extra2': 'client extra2'},
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


async def test_trivial_validator_in_array(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/empty',
        data=json.dumps({'field1': 'smth', 'unordered_set': [2]}),
    )
    assert response.status_code == 200
    assert response.json() == {'field1': 'smth'}


async def test_trivial_validator_in_array_error(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/empty',
        data=json.dumps({'field1': 'smth', 'unordered_set': [0]}),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Parse error at pos 38, path \'unordered_set.[0]\': '
            'out of bounds, must be 1 (limit) <= 0 (value), '
            'the latest token was 0'
        ),
    }
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


async def test_empty_post(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/empty', data=json.dumps({'field1': '123'}),
    )
    assert response.status_code == 200
    assert response.json() == {'field1': '123'}
    assert response.headers['ETag'] == '"etag-value"'
    assert response.headers['Expires'] == 'never'


async def test_empty_put(taxi_userver_sample):
    response = await taxi_userver_sample.put('autogen/empty')
    assert response.status_code == 405
