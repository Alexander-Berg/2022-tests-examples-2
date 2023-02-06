# pylint: disable=redefined-outer-name

import datetime
import decimal

import aiohttp
import pytest

from taxi import config
from taxi import discovery
from taxi.billing import clients as billing_clients
from taxi.billing.clients import models


@pytest.fixture
async def client(loop):
    class Config(config.Config):
        BILLING_ORDERS_CLIENT_QOS = {
            '__default__': {'attempts': 5, 'timeout-ms': 500},
        }

    session = aiohttp.ClientSession(loop=loop)
    yield billing_clients.BillingOrdersApiClient(
        service=discovery.find_service('billing_orders'),
        session=session,
        config=Config(),
        api_token='secret',
    )
    await session.close()


async def test_billing_orders_client(client, mockserver, response_mock):
    @mockserver.json_handler('/billing-orders/v1/process_event')
    def patch_request(request, *args, **kwargs):
        assert request.method == 'POST'
        assert request.headers.get('YaTaxi-Api-Key') == 'secret'
        return {'doc': {'id': 1002}}

    request = models.billing_orders.ProcessDocRequest(
        data={},
        event_at=datetime.datetime.utcnow(),
        external_event_ref='order_completed/quas-wex-exort',
        external_obj_id='alias_id/alias_id',
        kind='order_completed',
        service='billing-orders',
    )
    response = await client.process_event(request)
    assert patch_request.times_called == 1
    expected_response = models.billing_orders.ProcessDocResponse(doc_id=1002)
    assert response == expected_response


async def test_v1_execute(client, mockserver, response_mock):
    @mockserver.json_handler('/billing-orders/v1/execute')
    def patch_request(request, *args, **kwargs):
        assert request.method == 'POST'
        assert request.headers.get('YaTaxi-Api-Key') == 'secret'
        resp = request.json
        resp.update(topic='Hi', doc_id=6, created='2020-06-28T00:00:00+00:00')
        return resp

    now = datetime.datetime.now(tz=datetime.timezone.utc)
    request = models.billing_orders.V1ExecuteRequest(
        data={},
        event_at=now,
        external_ref='driver_mode_subscription',
        kind='order_completed',
    )
    response = await client.v1_execute(request)
    assert patch_request.times_called == 1

    expected_response = models.billing_orders.V1ExecuteResponse(
        data={},
        event_at=now,
        external_ref='driver_mode_subscription',
        kind='order_completed',
        topic='Hi',
        doc_id=6,
        created=datetime.datetime(2020, 6, 28, tzinfo=datetime.timezone.utc),
    )
    assert response == expected_response


def test_fee_update():
    def _test(fee, amount, expected):
        assert fee.add_amount(amount) == expected

    _test(
        billing_clients.models.billing_orders.Fee(
            'agreement',
            decimal.Decimal(12),
            'currency',
            'entity',
            'sub_account',
        ),
        decimal.Decimal(12),
        billing_clients.models.billing_orders.Fee(
            'agreement',
            decimal.Decimal(24),
            'currency',
            'entity',
            'sub_account',
        ),
    )
