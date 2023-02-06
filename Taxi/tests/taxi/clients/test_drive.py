# pylint: disable=redefined-outer-name, protected-access
import aiohttp
import pytest

from taxi import config as taxi_config
from taxi import settings as taxi_settings
from taxi.clients import drive
from taxi.clients import tvm


@pytest.fixture
async def config(db):
    return taxi_config.Config(db)


@pytest.fixture
async def settings():
    return taxi_settings.Settings()


@pytest.fixture
def tvm_client(simple_secdist, aiohttp_client, patch, config):
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
async def client(loop, config, settings, simple_secdist, tvm_client):
    session = aiohttp.ClientSession(loop=loop)
    yield drive.DriveClient(
        config=config,
        session=session,
        tvm_client=tvm_client,
        settings=settings,
    )
    await session.close()


async def test_client(client, mockserver):
    @mockserver.json_handler('/drive/api/b2b/accounts/descriptions')
    async def _response(*args, **kwargs):
        return {}

    await client._request(
        'GET',
        '/api/b2b/accounts/descriptions',
        params={},
        retries_cnt=10,
        retry_interval=0,
        timeout=0,
        headers={},
    )

    assert _response.has_calls


async def test_prestable_switch(
        client,
        settings,
        config,
        patch_aiohttp_session,
        response_mock,
        mockserver,
):
    @mockserver.json_handler('/drive/api/b2b/accounts/descriptions')
    async def stable_response(*args, **kwargs):
        return {}

    @patch_aiohttp_session(
        'http://prestable_url/api/b2b/accounts/descriptions',
    )
    def prestable_response(*args, **kwargs):
        return response_mock()

    config.CORP_DRIVE_USE_PRESTABLE = True
    settings.DRIVE_PRESTABLE_URL = 'http://prestable_url'
    await client._request(
        'GET',
        '/api/b2b/accounts/descriptions',
        params={},
        retries_cnt=10,
        retry_interval=0,
        timeout=0,
        headers={},
    )

    assert not stable_response.has_calls
    assert prestable_response.calls

    config.CORP_DRIVE_USE_PRESTABLE = False
    await client._request(
        'GET',
        '/api/b2b/accounts/descriptions',
        params={},
        retries_cnt=10,
        retry_interval=0,
        timeout=0,
        headers={},
    )
    assert not prestable_response.calls
    assert stable_response.has_calls


async def test_retry_timeout(client, mockserver):
    retries_cnt = 4

    @mockserver.json_handler('/drive/api/b2b/accounts/descriptions')
    async def _response(*args, **kwargs):
        return mockserver.make_response(
            json={'message': 'Message', 'code': 'ERROR_CODE'}, status=504,
        )

    with pytest.raises(drive.RequestRetriesExceeded):
        await client._request(
            'GET',
            '/api/b2b/accounts/descriptions',
            params={},
            retries_cnt=retries_cnt,
            retry_interval=0,
            timeout=0,
            headers={},
        )

    assert _response.has_calls
    assert _response.times_called == retries_cnt
