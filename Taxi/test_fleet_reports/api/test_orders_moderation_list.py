import aiohttp.web
import pytest


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success(
        web_app_client,
        headers,
        mock_parks,
        mock_api7,
        mock_fleet_transactions_api,
        mock_driver_orders,
        load_json,
):
    stub = load_json('success.json')

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['drivers']['request']
        return aiohttp.web.json_response(stub['drivers']['response'])

    @mock_driver_orders('/v1/parks/orders/list')
    async def _list_orders(request):
        assert request.json == stub['orders']['request']
        return aiohttp.web.json_response(stub['orders']['response'])

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_order_transactions(request):
        assert request.json == stub['transactions']['request']
        return aiohttp.web.json_response(stub['transactions']['response'])

    response = await web_app_client.post(
        '/reports-api/v1/orders/moderation/list',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
