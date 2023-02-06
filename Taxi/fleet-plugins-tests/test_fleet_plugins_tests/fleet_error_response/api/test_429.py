import aiohttp.web


async def test_external(web_app_client, mock_fleet_transactions_api):
    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _v1_driver_balances_list(request):
        return aiohttp.web.json_response(status=429, content_type='text/plain')

    response = await web_app_client.post('/fleet_error_response/429/external')

    assert response.status == 429


async def test_internal(web_app_client):
    response = await web_app_client.post(
        '/fleet_error_response/429/internal?throw_429=true',
    )
    assert response.status == 429

    response = await web_app_client.post(
        '/fleet_error_response/429/internal?throw_429=false',
    )
    assert response.status == 200
