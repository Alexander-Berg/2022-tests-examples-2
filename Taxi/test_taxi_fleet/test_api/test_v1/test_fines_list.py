import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_fines, mock_api7, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_fines('/v1/list-by-cars')
    async def _list_by_cars(request):
        assert request.json == stub['fines_request']
        return aiohttp.web.json_response(stub['fines_response'])

    @mock_api7('/v1/parks/cars/list')
    async def _list_cars(request):
        assert request.json == stub['api7_request_cars']
        return aiohttp.web.json_response(stub['api7_response_car'])

    response = await web_app_client.post(
        '/api/v1/fines/list', headers=headers, json={},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
