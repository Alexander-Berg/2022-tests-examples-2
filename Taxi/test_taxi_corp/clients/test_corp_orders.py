# pylint: disable=redefined-outer-name, protected-access
import pytest

from taxi import config
from taxi.clients import http_client
from taxi.clients import tvm

from taxi_corp.clients import corp_orders


@pytest.fixture
async def client(loop, db, simple_secdist):
    async with http_client.HTTPClient(loop=loop) as session:
        config_ = config.Config(db)
        yield corp_orders.CorpOrdersClient(
            config=config_,
            session=session,
            tvm_client=tvm.TVMClient(
                service_name='corp-orders',
                secdist=simple_secdist,
                config=config_,
                session=session,
            ),
        )


@pytest.mark.parametrize(
    ['params'],
    [
        pytest.param(
            {
                'client_id': 'client_id',
                'user_id': 'user_id',
                'limit': 100,
                'offset': 0,
            },
            id='simple get',
        ),
    ],
)
async def test_orders_eats_find(patch, client, params):
    expected_location = '/v1/orders/eats/find'

    @patch('taxi_corp.clients.corp_orders.CorpOrdersClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert params == kwargs['params']
        return {'orders': []}

    await client.find_eats_orders(params)
    assert _request.calls
