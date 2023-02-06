# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import asyncio
import json

import aiohttp
import pytest

from taxi import config
from taxi.clients import passport
from taxi.clients import tvm


@pytest.fixture
def tvm_client(simple_secdist, aiohttp_client, patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='corp-cabinet',
        secdist=simple_secdist,
        config=config,
        session=aiohttp_client,
    )


@pytest.fixture
def client(test_taxi_app, tvm_client):
    return passport.PassportClient(
        settings=test_taxi_app.settings,
        session=test_taxi_app.session,
        tvm=tvm_client,
        retry_intervals=[0.05, 0.1, 0.15],
    )


@pytest.mark.parametrize(
    ['origin', 'expected'],
    [
        ('business.taxi.yandex.com', 'yandex.com'),
        ('yango.delivery', 'yango.delivery'),
    ],
)
async def test_origin_match(client, origin, expected):
    assert expected == client._get_cookie_host(origin)


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, asyncio.TimeoutError],
)
async def test_request_raise_exc(client, patch, exception_type):
    @patch('aiohttp.ClientSession.get')
    async def _get(*args, **kwargs):
        raise exception_type()

    with pytest.raises(passport.InternalError):
        await client._request_bb_method(
            'some_method', '192.168.1.1', some_param='my_super_param',
        )


@pytest.mark.parametrize(
    'error_value, exception_type',
    [
        ('ACCESS_DENIED', passport.PermissionDeniedError),
        ('INVALID_PARAMS', passport.InvalidRequestError),
        ('DB_FETCHFAILED', passport.InternalError),
        ('DB_EXCEPTION', passport.InternalError),
        ('UNKNOWN', passport.InternalError),
    ],
)
async def test_request_error(
        client, patch, response_mock, error_value, exception_type,
):
    @patch('aiohttp.ClientSession.get')
    async def _get(*args, **kwargs):
        data = {'exception': {'value': error_value}}
        return response_mock(text=json.dumps(data), status=200)

    with pytest.raises(exception_type):
        await client._request_bb_method(
            'some_method', '192.168.1.1', some_param='my_super_param',
        )


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, asyncio.TimeoutError],
)
async def test_request_retryable_exc(
        client, patch, response_mock, exception_type,
):
    try_number = 0

    @patch('aiohttp.ClientSession.get')
    async def _get(*args, **kwargs):
        nonlocal try_number
        if try_number < 2:
            try_number += 1
            raise exception_type()
        return response_mock(text=json.dumps({'success': True}), status=200)

    result = await client._request_bb_method(
        'some_method', '192.168.1.1', some_param='my_super_param',
    )
    assert result == {'success': True}


@pytest.mark.parametrize(
    'error_value', ['DB_FETCHFAILED', 'DB_EXCEPTION', 'UNKNOWN'],
)
async def test_request_retryable_errors(
        client, patch, response_mock, error_value,
):
    try_number = 0

    @patch('aiohttp.ClientSession.get')
    async def _get(*args, **kwargs):
        nonlocal try_number
        if try_number < 2:
            try_number += 1
            data = {'exception': {'value': error_value}}
        else:
            data = {'success': True}

        return response_mock(text=json.dumps(data), status=200)

    result = await client._request_bb_method(
        'some_method', '192.168.1.1', some_param='my_super_param',
    )
    assert result == {'success': True}


@pytest.mark.parametrize(
    'error_value, exception_type',
    [
        ('ACCESS_DENIED', passport.PermissionDeniedError),
        ('INVALID_PARAMS', passport.InvalidRequestError),
    ],
)
async def test_request_single_try_errors(
        client, patch, response_mock, error_value, exception_type,
):
    try_number = 0

    @patch('aiohttp.ClientSession.get')
    async def _get(*args, **kwargs):
        nonlocal try_number
        if try_number < 2:
            try_number += 1
            data = {'exception': {'value': error_value}}
        else:
            data = {'success': True}

        return response_mock(text=json.dumps(data), status=200)

    with pytest.raises(exception_type):
        await client._request_bb_method(
            'some_method', '192.168.1.1', some_param='my_super_param',
        )


@pytest.mark.parametrize(
    'source,expected', [('abcdefg', '...'), ('', ''), (None, None)],
)
def test_obfuscate_oauth_token(source, expected):
    result = passport._obfuscate_oauth_token(source)

    if source is None:
        assert result is expected
    else:
        assert result == expected


@pytest.mark.parametrize(
    'source,expected',
    [
        ('a.b.c|d.e|f.g.hmac', 'a.b.c|d.e|f.g.XXXXXXXXXXXXXXXXXXXXXXXXXXX'),
        ('s|m|t|h', 'XXXXXXXXXXXXXXXXXXXXXXXXXXX'),
        ('', ''),
        (None, None),
    ],
)
def test_obfuscate_sessionid(source, expected):
    result = passport._obfuscate_sessionid(source)

    if source is None:
        assert result is expected
    else:
        assert result == expected


@pytest.mark.parametrize(
    'obfuscator,source,num_calls_expected',
    [
        ('_obfuscate_oauth_token', {'oauth_token': 'def'}, 1),
        ('_obfuscate_oauth_token', {'oauth_token': 'def', 'name': 'jon'}, 1),
        ('_obfuscate_oauth_token', {'name': 'jon'}, 0),
        ('_obfuscate_sessionid', {'sessionid': 'def'}, 1),
        ('_obfuscate_sessionid', {'sessionid': 'def', 'name': 'jon'}, 1),
        ('_obfuscate_sessionid', {'sessionid': 'def', 'sid': 'ghi'}, 2),
        ('_obfuscate_sessionid', {'name': 'jon'}, 0),
    ],
)
def test_obfuscate_secrets_oauth_token(
        obfuscator, source, num_calls_expected, patch,
):
    @patch('taxi.clients.passport.' + obfuscator)
    def obfus_patch(source):
        pass

    passport._obfuscate_secrets(source)

    assert len(obfus_patch.calls) == num_calls_expected


@pytest.mark.parametrize(
    'source',
    [
        {'oauth_token': 'def'},
        {'sessionid': 'def', 'name': 'jon'},
        {'sessionid': 'def', 'sid': 'ghi'},
        {'name': 'jon'},
    ],
)
def test_obfuscate_secrets_preserves_source_keys(source):
    result = passport._obfuscate_secrets(source)

    assert result.keys() == source.keys()
