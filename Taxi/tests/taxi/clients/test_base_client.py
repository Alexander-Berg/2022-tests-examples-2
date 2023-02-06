# pylint: disable=redefined-outer-name
import asyncio

import aiohttp
import pytest

from taxi.clients import tvm
from taxi.clients.helpers import base_client
from taxi.clients.helpers import errors


@pytest.fixture
def client(test_taxi_app, simple_secdist):
    return base_client.BaseClient(
        session=test_taxi_app.session,
        tvm_client=tvm.TVMClient(
            service_name='partner_contracts',
            secdist=simple_secdist,
            config=test_taxi_app.config,
            session=test_taxi_app.session,
        ),
        retry_intervals=[0.05, 0.1, 0.15],
    )


async def test_request(client, patch, response_mock):
    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        return response_mock(text='{}', status=200)

    result = await client.request('method', 'url')
    assert result.body == {}
    assert result.headers == {'Content-Type': 'application/json'}


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, asyncio.TimeoutError],
)
async def test_request_raise_exc(client, patch, exception_type):
    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        raise exception_type()

    with pytest.raises(errors.ClientConnectionError):
        await client.request('method', 'url')


async def test_request_error(client, patch, response_mock):
    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        return response_mock(text='{}', status=400)

    with pytest.raises(errors.BadRequestError):
        await client.request('method', 'url')


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, asyncio.TimeoutError],
)
async def test_request_retryable_exc(
        client, patch, response_mock, exception_type,
):
    try_number = 0

    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        nonlocal try_number
        if try_number < 2:
            try_number += 1
            raise exception_type()
        return response_mock(text='{}', status=200)

    result = await client.request('method', 'url')
    assert result.body == {}
