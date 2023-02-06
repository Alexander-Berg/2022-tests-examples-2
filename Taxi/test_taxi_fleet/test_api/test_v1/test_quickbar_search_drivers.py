import aiohttp.web


async def test_success(web_app_client, headers, mockserver, load_json):

    parks_stub = load_json('parks_success.json')
    service_stub = load_json('service_success.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_driver_profiles_retrieve(request):
        assert request.json == parks_stub['request']
        return aiohttp.web.json_response(parks_stub['response'])

    response = await web_app_client.post(
        '/api/v1/quickbar/search/drivers',
        headers=headers,
        json=service_stub['request'],
    )
    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
