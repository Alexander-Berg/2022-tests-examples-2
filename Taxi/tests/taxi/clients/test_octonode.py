# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import asyncio

import aiohttp
import pytest

from taxi import config
from taxi.clients import octonode


@pytest.fixture
def client(db, loop):
    session = aiohttp.ClientSession(loop=loop)
    return octonode.OctonodeClient(session, config.Config(db))


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, asyncio.TimeoutError],
)
@pytest.mark.nofilldb()
async def test_request_try_and_fail(client, patch, exception_type):
    @patch('aiohttp.ClientSession.request')
    async def _request(*args, **kwargs):
        raise exception_type()

    with pytest.raises(octonode.RequestRetriesExceeded):
        await client.create_session({})


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
        if count < config.Config.OCTONODE_RETRIES:
            raise exception_type()
        else:
            return response_mock(json={'session_id': 'SESSION_ID_UUID'})

    await client.create_session({})
