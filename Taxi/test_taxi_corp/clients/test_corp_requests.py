# pylint: disable=redefined-outer-name
# pylint: disable=C0103
import pytest

from taxi.clients import http_client
from taxi.clients.helpers import base_client

BASE_URL = '$mockserver/corp-requests'


@pytest.fixture
async def client(loop, db, simple_secdist):
    from taxi import config
    from taxi.clients import tvm
    from taxi_corp.clients import corp_requests

    async with http_client.HTTPClient(loop=loop) as session:
        config_ = config.Config(db)
        yield corp_requests.CorpRequestsClient(
            session=session,
            tvm_client=tvm.TVMClient(
                service_name='developers',
                secdist=simple_secdist,
                config=config_,
                session=session,
            ),
        )


async def test_v1_client_request_draft_get(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.v1_client_request_draft_get(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/client-request-draft',
        },
    ]


async def test_v1_client_request_draft_put(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.v1_client_request_draft_put(
        client_id='client_id', body={'k': 'v'},
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'client_id': 'client_id'},
                'json': {'k': 'v'},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'PUT',
            'url': f'{BASE_URL}/v1/client-request-draft',
        },
    ]


async def v1_client_request_draft_commit_post(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return {}

    await client.v1_client_request_draft_put(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'POST',
            'url': f'{BASE_URL}/v1/client-request-draft/commit',
        },
    ]
