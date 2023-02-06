# pylint: disable=redefined-outer-name
import pytest

from eats_integration_offline_orders.components.pos import iiko_client
from eats_integration_offline_orders.generated.service.swagger.models import (
    api as api_module,
)

TABLE_POS_ID = '1'


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'restaurants.sql'],
)
async def test_iiko_get_check(
        web_context, place_id, patch, load_json, pos_ws_message_factory,
):
    @patch(
        'eats_integration_offline_orders.clients.'
        'websocket_client.WebSocketClient._request',
    )
    async def _request(ws_id, msg_data, **kwargs):
        assert msg_data['headers']['X-API-Version'] == '2.1'
        assert msg_data['headers']['method'] == 'get_table'
        assert msg_data['headers']['args'] == {'table_id': TABLE_POS_ID}
        return pos_ws_message_factory(body=load_json('orders.json'))

    client = iiko_client.IIKOClient(web_context)
    data = await client.get_check(place_id, TABLE_POS_ID)
    assert isinstance(data, api_module.PosOrders)


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'restaurants.sql'],
)
async def test_iiko_freeze_order(
        web_context,
        place_id,
        order_uuid,
        patch,
        pos_ws_message_factory,
        load_json,
):
    @patch(
        'eats_integration_offline_orders.clients.'
        'websocket_client.WebSocketClient._request',
    )
    async def _request(ws_id, msg_data, **kwargs):
        assert msg_data['headers']['X-API-Version'] == '2.1'
        assert msg_data['headers']['method'] == 'freeze_order'
        assert msg_data['headers']['args'] == {'order_uuid': order_uuid}
        return pos_ws_message_factory(
            body=load_json('orders.json')['orders'][0],
        )

    client = iiko_client.IIKOClient(web_context)
    data = await client.freeze_order(place_id, order_uuid)
    assert isinstance(data, api_module.PosOrder)


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'restaurants.sql', 'orders.sql'],
)
async def test_iiko_order_paid(
        web_context,
        place_id,
        order_uuid,
        patch,
        load_json,
        pos_ws_message_factory,
):
    @patch(
        'eats_integration_offline_orders.clients.'
        'websocket_client.WebSocketClient._request',
    )
    async def _request(ws_id, msg_data, **kwargs):
        assert msg_data['headers']['X-API-Version'] == '2.1'
        assert msg_data['headers']['method'] == 'pay_order'
        assert msg_data['headers']['args'] == {'order_uuid': order_uuid}
        assert msg_data['body'] == load_json('order_paid_request_body.json')
        return pos_ws_message_factory(body={})

    client = iiko_client.IIKOClient(web_context)
    await client.send_payment_result(place_id, order_uuid, True)


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'restaurants.sql'],
)
async def test_iiko_apply_loyalty(
        web_context,
        restaurant_slug,
        order_uuid,
        patch,
        pos_ws_message_factory,
):
    loyalty_identifier = '+71234567890'

    @patch(
        'eats_integration_offline_orders.clients.'
        'websocket_client.WebSocketClient._request',
    )
    async def _request(ws_id, msg_data, **kwargs):
        assert msg_data['headers']['X-API-Version'] == '2.1'
        assert msg_data['headers']['method'] == 'apply_loyalty'
        assert msg_data['headers']['args'] == {'order_uuid': order_uuid}
        assert msg_data['body']['loyalty_identifier'] == loyalty_identifier
        return pos_ws_message_factory(body={})

    client = iiko_client.IIKOClient(web_context)
    await client.apply_loyalty(restaurant_slug, order_uuid, loyalty_identifier)


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'db_iiko_transport_meta.sql'],
)
async def test_iiko_append_items_create_order(
        web_context, place_id, mock_iiko_cloud,
):
    @mock_iiko_cloud('/api/1/terminal_groups/is_alive')
    async def _iiko_cloud_terminal_groups_is_alive(request):
        return {
            'correlationId': 'd7ca58cd-ff9a-4748-8f7e-deb19a9b14dd',
            'isAliveStatus': [
                {
                    'isAlive': True,
                    'terminalGroupId': '00000000-0000-0000-term-00000000001',
                    'organizationId': '00000000-0000-0000-orga-00000000001',
                },
            ],
        }

    @mock_iiko_cloud('/api/1/reserve/available_restaurant_sections')
    async def _iiko_cloud_available_restaurant_sections(request):
        return {
            'correlationId': '4af2fdbc-aeed-49a8-aae7-a189a09ea9d0',
            'restaurantSections': [
                {
                    'id': '81cb8be7-791b-4f80-9c77-f463fbb0f2ce',
                    'terminalGroupId': '00000000-0000-0000-term-00000000001',
                    'name': 'Банкет',
                    'tables': [
                        {
                            'id': '83f9adc0-d76a-4e0e-9bb5-2cf68a80cef2',
                            'number': 11,
                            'name': 'Table 11',
                            'seatingCapacity': 0,
                            'revision': 1652460987654,
                            'isDeleted': False,
                        },
                    ],
                    'schema': None,
                },
                {
                    'id': '9a091cd4-78dc-46d6-b797-1e0ddb58c00c',
                    'terminalGroupId': '00000000-0000-0000-term-00000000001',
                    'name': 'Бар',
                    'tables': [
                        {
                            'id': '2812971f-8391-4456-a935-23258e039a1d',
                            'number': 1,
                            'name': 'Table 1',
                            'seatingCapacity': 0,
                            'revision': 1652460987654,
                            'isDeleted': False,
                        },
                    ],
                    'schema': None,
                },
            ],
            'revision': 1652460987654,
        }

    @mock_iiko_cloud('/api/1/access_token')
    async def _iiko_cloud_access_token(request):
        api_login = request.json['apiLogin']
        assert api_login == '77c54078bb024d39ad5cb8193fe62035'
        return {
            'correlationId': 'd7ca58cd-ff9a-4748-8f7e-deb19a9b14dd',
            'token': '4e6f81a8-891b-4e35-b4ed-f4c10f9a4987',
        }

    @mock_iiko_cloud('/api/1/order/create')
    async def _iiko_cloud_order_create(request):
        return {
            'correlationId': 'correlation_id',
            'orderInfo': {
                'id': 'new_order_id',
                'organizationId': '00000000-0000-0000-orga-00000000001',
                'timestamp': 0,
                'creationStatus': 'Success',
            },
        }

    client = iiko_client.IIKOClient(web_context)
    result = await client.order_create(
        place_id=place_id,
        table_pos_id=TABLE_POS_ID,
        idempotency_token='idempotency_token',
        items=[api_module.NewOrderItem(id='test order', quantity=1)],
    )
    assert result == 'new_order_id'
