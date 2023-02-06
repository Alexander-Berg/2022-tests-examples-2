import aiohttp.web


async def test_success(web_app_client, headers, mock_api7, load_json):
    stub = load_json('success.json')

    @mock_api7('/v1/parks/cars/list')
    async def _list_cars(request):
        assert request.json == stub['api7_request']
        return aiohttp.web.json_response(stub['api7_response'])

    response = await web_app_client.post(
        '/api/v1/cars/list', headers=headers, json={'limit': 2},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
