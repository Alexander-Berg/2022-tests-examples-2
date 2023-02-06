import aiohttp.web
import pytest


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success(web_app_client, headers, mock_api7, load_json):
    stub = load_json('success.json')

    @mock_api7('/v1/parks/cars/list')
    async def _list_cars(request):
        assert request.json == stub['cars']['request']
        return aiohttp.web.json_response(stub['cars']['response'])

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['drivers']['request']
        return aiohttp.web.json_response(stub['drivers']['response'])

    response = await web_app_client.post(
        '/reports-api/v1/summary/cars/list',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
