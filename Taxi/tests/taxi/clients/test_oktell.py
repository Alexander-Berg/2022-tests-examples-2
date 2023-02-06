# pylint: disable=redefined-outer-name
import asyncio
import logging

import aiohttp
import pytest

from taxi import config
from taxi.clients import oktell

DEFAULT_USER = {
    'login': 'login1',
    'password': 'secret_password',
    'info': '',
    'role': 'диспетчер',
    'name': 'Тестовый',
    'callcenter': 'cc1',
}

logger = logging.getLogger(__name__)


@pytest.fixture
async def client(db, loop):
    class Config(config.Config):
        OKTELL_HOSTS = ['1', '2']
        OKTELL_CLIENT_QOS = {'attempts': 3, 'timeout_ms': 200}

    secdist = {
        'settings_override': {
            'OKTELL_NGINX_BASIC_AUTH_PASSWORD': 'default_password',
        },
    }
    return oktell.OktellClient(
        session=aiohttp.ClientSession(loop=loop),
        config=Config(db),
        secdist=secdist,
    )


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, asyncio.TimeoutError],
)
@pytest.mark.nofilldb()
async def test_request_try_and_fail(
        client, patch, exception_type, response_mock,
):
    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        raise exception_type()

    for host in client.config.OKTELL_HOSTS:
        with pytest.raises(oktell.RequestRetriesExceeded):
            await client.create_user(
                host,
                DEFAULT_USER['login'],
                DEFAULT_USER['password'],
                DEFAULT_USER['info'],
                DEFAULT_USER['role'],
                DEFAULT_USER['name'],
                DEFAULT_USER['callcenter'],
            )


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, asyncio.TimeoutError],
)
@pytest.mark.nofilldb()
async def test_request_retry_and_succeed(
        client, patch, exception_type, response_mock,
):
    count = 0

    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        nonlocal count
        count += 1
        logger.debug('c=%s', count)
        if count < client.config.OKTELL_CLIENT_QOS['attempts']:
            raise exception_type()
        else:
            count = 0
            return response_mock(status=200)

    for host in client.config.OKTELL_HOSTS:
        await client.create_user(
            host,
            DEFAULT_USER['login'],
            DEFAULT_USER['password'],
            DEFAULT_USER['info'],
            DEFAULT_USER['role'],
            DEFAULT_USER['name'],
            DEFAULT_USER['callcenter'],
        )


@pytest.mark.nofilldb()
async def test_check_user(client, patch, response_mock):
    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        return response_mock(status=200, text='active')

    for host in client.config.OKTELL_HOSTS:
        res = await client.check_user(host, DEFAULT_USER['login'])
        assert res == 'active'


@pytest.mark.nofilldb()
async def test_check_user_bad_request(client, patch, response_mock):
    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        return response_mock(status=404)

    for host in client.config.OKTELL_HOSTS:
        res = await client.check_user(host, DEFAULT_USER['login'])
        assert res == 'not_found'
