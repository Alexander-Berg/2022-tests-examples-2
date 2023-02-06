# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from userver_sample_plugins.generated_tests import *  # noqa


async def test_echo(taxi_userver_sample):
    test_header_name = 'Echo-Test-Header'
    test_header_value = 'test header value'

    params = {'hello': 'world'}
    headers = {test_header_name: test_header_value}
    response = await taxi_userver_sample.get(
        'echo', params=params, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == params
    assert response.headers.get(test_header_name) == test_header_value


async def test_echo_aiohttp(taxi_userver_sample_aiohttp):
    test_header_name = 'Echo-Test-Header'
    test_header_value = 'test header value'

    params = {'hello': 'world'}
    headers = {test_header_name: test_header_value}
    response = await taxi_userver_sample_aiohttp.get(
        'echo', params=params, headers=headers,
    )
    async with response:
        assert response.status == 200
        assert (await response.json(content_type=None)) == params
        assert response.headers.get(test_header_name) == test_header_value


async def test_mongo_set_get(taxi_userver_sample):
    params_set = {'hello': 'world', 'foo': 'bar'}
    response = await taxi_userver_sample.get('mongo-set', params=params_set)
    assert response.status_code == 200
    assert response.content == b''
    params_get = {'hello': 1, 'foo': 1}
    response = await taxi_userver_sample.get('mongo-get', params=params_get)
    assert response.status_code == 200
    assert response.json() == {'foo': ['bar'], 'hello': ['world']}


async def test_mongo_set_get_multi(taxi_userver_sample):
    params_set = {'foo': ['bar', 'fiz', 'baz']}
    response = await taxi_userver_sample.get('mongo-set', params=params_set)
    assert response.status_code == 200
    assert response.content == b''
    params_get = {'foo': 1}
    response = await taxi_userver_sample.get('mongo-get', params=params_get)
    assert response.status_code == 200
    assert response.json() == params_set


async def test_mongo_nonexist(taxi_userver_sample):
    params_get = {'nonexist_field': 1}
    response = await taxi_userver_sample.get('mongo-get', params=params_get)
    assert response.status_code == 500
