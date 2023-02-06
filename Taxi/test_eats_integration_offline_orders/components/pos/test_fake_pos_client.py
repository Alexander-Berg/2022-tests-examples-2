from eats_integration_offline_orders.components.pos import fake_pos_client
from eats_integration_offline_orders.generated.service.swagger.models import (
    api as api_module,
)


async def test_fake_pos_client_get_check(web_context):

    data = await fake_pos_client.FakePOSClient(web_context).get_check(
        place_id='fake_place_id', table_pos_id='fake_table_id',
    )
    assert isinstance(data, api_module.PosOrders)


async def test_fake_pos_client_freeze_check(web_context):

    data = await fake_pos_client.FakePOSClient(web_context).freeze_order(
        place_id='fake_place_id', order_uuid='fake_order_uuid',
    )
    assert isinstance(data, api_module.PosOrder)
