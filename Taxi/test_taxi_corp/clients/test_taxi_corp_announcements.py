# pylint: disable=redefined-outer-name, protected-access
import asyncio

import pytest

from taxi import config
from taxi import discovery
from taxi.clients import http_client
from taxi.clients import tvm

from taxi_corp.clients import taxi_corp_announcements


@pytest.fixture
async def client(loop, db, simple_secdist):
    async with http_client.HTTPClient(loop=loop) as session:
        config_ = config.Config(db)
        yield taxi_corp_announcements.CorpAnnouncementsClient(
            config=config_,
            session=session,
            tvm_client=tvm.TVMClient(
                service_name=taxi_corp_announcements.TVM_SERVICE_NAME,
                secdist=simple_secdist,
                config=config_,
                session=session,
            ),
        )


async def test_timeout_error(
        client, patch, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(
        discovery.find_service('taxi_corp_announcements').url, 'POST',
    )
    def patch_request(method, url, **kwargs):
        raise asyncio.TimeoutError()

    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    with pytest.raises(taxi_corp_announcements.RequestRetriesExceeded) as exc:
        await client._request(
            'POST', '/location', params={}, data={}, headers={},
        )

    assert 'retries' in str(exc)
    assert len(patch_request.calls) == 3
