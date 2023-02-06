# pylint: disable=redefined-outer-name, protected-access
import aiohttp
import pytest

from taxi import config
from taxi.clients import billing_replication
from taxi.clients import tvm


@pytest.fixture
async def client(loop, db, simple_secdist):
    session = aiohttp.ClientSession(loop=loop)
    config_ = config.Config(db)
    yield billing_replication.BillingReplicationClient(
        session=session,
        tvm_client=tvm.TVMClient(
            service_name='billing-replication',
            secdist=simple_secdist,
            config=config_,
            session=session,
        ),
    )
    await session.close()


@pytest.mark.parametrize(
    ['client_id'], [pytest.param('some_client_id', id='some_client_id')],
)
async def test_get_park_info(patch, client, client_id):
    expected_location = '/person/'

    @patch(
        'taxi.clients.billing_replication.BillingReplicationClient._request',
    )
    async def _request(url, method, *args, **kwargs):
        assert method == 'GET'
        assert url == expected_location
        assert kwargs['params']['client_id'] == client_id

    await client.get_park_info(client_id)
    assert _request.calls


@pytest.mark.parametrize(
    ['client_id', 'contract_type'],
    [pytest.param('some_client_id', 'GENERAL', id='some_client_id')],
)
async def test_get_contracts(patch, client, client_id, contract_type):
    expected_location = '/contract/'

    @patch(
        'taxi.clients.billing_replication.BillingReplicationClient._request',
    )
    async def _request(url, method, *args, **kwargs):
        assert method == 'GET'
        assert url == expected_location
        assert kwargs['params']['client_id'] == client_id
        assert kwargs['params']['type'] == contract_type

    await client.get_contracts(client_id, contract_type)
    assert _request.calls


@pytest.mark.parametrize(
    ['client_ids', 'service_ids'],
    [
        pytest.param(['1', '2'], None, id='send only clients'),
        pytest.param(
            ['1', '2', '3'], ['135'], id='send clients with services',
        ),
    ],
)
async def test_get_clients_contracts(patch, client, client_ids, service_ids):
    expected_location = '/v1/contracts/'

    @patch(
        'taxi.clients.billing_replication.BillingReplicationClient._request',
    )
    async def _request(url, method, *args, **kwargs):
        assert method == 'POST'
        assert url == expected_location
        assert kwargs['data']['client_ids'] == client_ids
        if service_ids is None:
            assert 'service_ids' not in kwargs['data']
        else:
            assert kwargs['data']['service_ids'] == service_ids

    await client.get_clients_contracts(client_ids, service_ids)
    assert _request.calls
