import aiohttp.web
import pytest


@pytest.mark.config(OPTEUM_MINI_REPORT_DRIVER_HOURS_SETTINGS={'hours': 100})
async def test_success(
        web_app_client,
        headers,
        mock_driver_orders,
        mock_fleet_transactions_api,
        mock_driver_supply_hours,
        load_json,
):
    stub = load_json('success.json')

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _balances_groups_list(request):
        assert request.json == stub['balances']['request']
        return aiohttp.web.json_response(stub['balances']['response'])

    @mock_driver_orders('/v1/parks/orders/list')
    async def _orders_list(request):
        if request.json.get('cursor'):
            return aiohttp.web.json_response(stub['orders']['response_2'])

        assert request.json == stub['orders']['request']
        return aiohttp.web.json_response(stub['orders']['response_1'])

    @mock_driver_supply_hours('/v1/parks/drivers-profiles/supply/retrieve')
    async def _v1_parks_drivers_profiles_supply_retrieve(request):
        assert request.json == stub['work_time']['request']
        return aiohttp.web.json_response(stub['work_time']['response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/income',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']


@pytest.mark.config(OPTEUM_MINI_REPORT_DRIVER_HOURS_SETTINGS={'hours': 1})
async def test_date_range(web_app_client, headers, load_json):
    stub = load_json('success.json')

    response = await web_app_client.post(
        '/api/v1/cards/driver/income',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 400
