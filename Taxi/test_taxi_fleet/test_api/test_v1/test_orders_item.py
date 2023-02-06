import aiohttp.web
import pytest


@pytest.mark.now('2020-06-10T00:00:00+03:00')
async def test_orders_item(
        web_app_client,
        headers,
        mockserver,
        mock_api7,
        mock_driver_orders,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success.json')

    @mock_driver_orders('/v1/parks/orders/list')
    async def _list_orders(request):
        assert request.json == stub['api7']['orders']['request']
        return aiohttp.web.json_response(stub['api7']['orders']['response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_driver_profiles_retrieve(request):
        assert request.json == stub['parks']['drivers']['request']
        return aiohttp.web.json_response(stub['parks']['drivers']['response'])

    @mock_api7('/v1/parks/cars/list')
    async def _list_cars(request):
        assert request.json == stub['api7']['cars']['request']
        return aiohttp.web.json_response(stub['api7']['cars']['response'])

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_order_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    response = await web_app_client.post(
        '/api/v1/orders/item',
        headers=headers,
        json=stub['service']['request'],
    )
    assert response.status == 200
    data = await response.json()
    assert data == stub['service']['response']
