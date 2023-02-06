# pylint: disable=redefined-outer-name
import pytest

from eats_integration_offline_orders.components.pos import rkeeper_client
from eats_integration_offline_orders.generated.service.swagger.models import (
    api as api_module,
)


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'restaurants.sql'],
)
async def test_rkeeper_get_check(
        web_context,
        place_id,
        table_pos_id,
        restaurant_slug,
        mockserver,
        load_json,
):
    @mockserver.handler('/rkeeper/table')
    def _get_check(request):
        assert request.query['pos_id'] == restaurant_slug
        assert request.query['table_id'] == table_pos_id
        assert 'X-API-Version' in request.headers
        assert 'Authorization' in request.headers
        return mockserver.make_response(json=load_json('orders.json'))

    client = rkeeper_client.RKeeperClient(web_context)
    data = await client.get_check(place_id, table_pos_id)
    assert isinstance(data, api_module.PosOrders)


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'restaurants.sql'],
)
async def test_rkeeper_freeze_order(
        web_context,
        place_id,
        restaurant_slug,
        order_uuid,
        mockserver,
        load_json,
):
    @mockserver.handler('/rkeeper/order/freeze')
    def _order_freeze(request):
        assert request.query['pos_id'] == restaurant_slug
        assert request.query['order_uuid'] == order_uuid
        assert 'X-API-Version' in request.headers
        assert 'Authorization' in request.headers
        return mockserver.make_response(
            json=load_json('orders.json')['orders'][0],
        )

    client = rkeeper_client.RKeeperClient(web_context)
    data = await client.freeze_order(place_id, order_uuid)
    assert isinstance(data, api_module.PosOrder)


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'restaurants.sql', 'orders.sql'],
)
async def test_rkeeper_order_paid(
        web_context, place_id, restaurant_slug, order_uuid, mockserver,
):
    @mockserver.handler('/rkeeper/order/paid')
    def _order_paid(request):
        assert request.query['pos_id'] == restaurant_slug
        assert request.query['order_uuid'] == order_uuid
        assert 'X-API-Version' in request.headers
        assert 'Authorization' in request.headers
        assert request.json['status']
        return mockserver.make_response()

    client = rkeeper_client.RKeeperClient(web_context)
    await client.send_payment_result(place_id, order_uuid, True)


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'restaurants.sql'],
)
async def test_rkeeper_apply_loyalty(
        web_context, restaurant_slug, order_uuid, mockserver,
):
    loyalty_identifier = '+71234567890'

    @mockserver.handler('/rkeeper/loyalty/apply')
    def _order_paid(request):
        assert request.query['pos_id'] == restaurant_slug
        assert request.query['order_uuid'] == order_uuid
        assert 'X-API-Version' in request.headers
        assert 'Authorization' in request.headers
        assert request.json['loyalty_identifier'] == loyalty_identifier
        return mockserver.make_response()

    client = rkeeper_client.RKeeperClient(web_context)
    await client.apply_loyalty(restaurant_slug, order_uuid, loyalty_identifier)
