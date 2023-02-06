import aiohttp.web


async def test_success(web_app_client, headers, mock_fleet_fines, load_json):
    stub = load_json('success.json')

    @mock_fleet_fines('/v1/stats-by-cars')
    async def _stats_by_cars(request):
        assert request.json == stub['fines_request']
        return aiohttp.web.json_response(stub['fines_response'])

    response = await web_app_client.post(
        '/api/v1/fines/stats', headers=headers, json={},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
