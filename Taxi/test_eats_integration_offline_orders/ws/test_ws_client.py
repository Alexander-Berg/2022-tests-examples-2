import asyncio

from aiohttp import web
import pytest

from eats_integration_offline_orders.clients import websocket_client
from eats_integration_offline_orders.internal import enums
from eats_integration_offline_orders.internal import types as local_types


async def test_ws_client_request(
        web_context, patch, place_id, table_pos_id, pos_ws_message_factory,
):
    @patch(
        'eats_integration_offline_orders.clients.'
        'websocket_client.WebSocketClient._request',
    )
    async def _request(ws_id, msg_data, **kwargs):
        assert 'message_uuid' in msg_data
        assert msg_data['headers'] == {
            'X-API-Version': '2.1',
            'method': 'some_method',
            'args': {'some_arg': 'arg_value'},
        }
        assert msg_data['type'] == enums.POSWsMessageType.REQUEST.value
        assert msg_data['body'] == {'some_data': 'data_value'}

        return pos_ws_message_factory(body={})

    response = await web_context.ws_client.request(
        ws_id=place_id,
        method='some_method',
        args={'some_arg': 'arg_value'},
        headers={'X-API-Version': '2.1'},
        body={'some_data': 'data_value'},
    )
    assert isinstance(response, local_types.POSWsMessage)


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['pos_ws_tokens.sql', 'restaurants.sql'],
)
async def test_ws_client_response(
        web_context, pos_ws_connection, place_id, table_pos_id,
):
    response = await web_context.ws_client.request(
        ws_id=place_id, method='get_table', args={'table_id': table_pos_id},
    )
    assert response
    assert isinstance(response, local_types.POSWsMessage)


async def test_ws_client_request_to_offline_pos(
        web_context, place_id, table_pos_id,
):
    with pytest.raises(websocket_client.WSClientNotConnected):
        await web_context.ws_client.request(
            ws_id=place_id,
            method='get_table',
            args={'table_id': table_pos_id},
        )


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={
        'ws_client_request_timeout': 0.1,
    },
)
async def test_ws_client_request_timeout(
        web_context, place_id, table_pos_id, patch,
):
    @patch(
        'eats_integration_offline_orders.components.'
        'pubsub.RedisPubSub.subscribe_for_response',
    )
    async def _response_mock(*args, **kwargs):
        class FakeChannel:
            name = 'channel_name'

            async def get_json(self):
                await asyncio.sleep(0.2)
                # if we are here timeout is broken
                assert False, 'HTTPRequestTimeout did not raise'

        return FakeChannel()

    @patch(
        'eats_integration_offline_orders.components.'
        'pubsub.RedisPubSub.requests_channel_subscribers',
    )
    async def _subscribers_mock(*args, **kwargs):
        return 1

    with pytest.raises(web.HTTPRequestTimeout):
        await web_context.ws_client.request(
            ws_id=place_id,
            method='get_table',
            args={'table_id': table_pos_id},
        )
