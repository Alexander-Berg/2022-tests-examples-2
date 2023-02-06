import aiohttp.web


async def test_success(web_app_client, headers, mock_api7, load_json):

    api7_stub = load_json('api7_success.json')
    service_stub = load_json('service_success.json')

    @mock_api7('/v1/parks/cars/list')
    async def _v1_parks_cars_list(request):
        assert request.json == api7_stub['request']
        return aiohttp.web.json_response(api7_stub['response'])

    response = await web_app_client.post(
        '/api/v1/quickbar/search/cars',
        headers=headers,
        json=service_stub['request'],
    )
    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
