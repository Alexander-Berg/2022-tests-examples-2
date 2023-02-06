# pylint: disable=redefined-outer-name,unused-variable
import bson
import pytest

from taxi import discovery
from taxi.clients import market_crm

from taxi_support_chat.generated.stq3 import stq_context
from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    ('chat_id', 'expected_puid', 'expected_orders_ids'),
    [
        (bson.ObjectId('5e285103779fb3831c8b4ad8'), 'market_yuid1', []),
        (
            bson.ObjectId('5e285103779fb3831c8b4ad9'),
            'market_yuid2',
            ['123456'],
        ),
        (
            bson.ObjectId('5e285103779fb3831c8b4a10'),
            'market_yuid2',
            ['123456', '654321'],
        ),
    ],
)
async def test_task(
        monkeypatch,
        patch_aiohttp_session,
        response_mock,
        stq3_context: stq_context.Context,
        chat_id,
        expected_puid,
        expected_orders_ids,
):
    service = discovery.find_service(market_crm.SERVICE_NAME)

    @patch_aiohttp_session(service.url)
    def mock_request(method, url, **kwargs):
        assert method == 'post'
        assert url == service.url + '/taxi/chat/newMessages'
        assert kwargs['json']['puid'] == expected_puid
        assert len(kwargs['json']['ordersIds']) == len(expected_orders_ids)
        for order_id in expected_orders_ids:
            assert order_id in kwargs['json']['ordersIds']
        return response_mock(status=200)

    await stq_task.market_notify_task(stq3_context, chat_id)

    assert mock_request.calls
