import aiohttp.web


async def test_success(web_app_client, headers, mock_fleet_parks, load_json):
    stub = load_json('success.json')

    @mock_fleet_parks('/v1/parks/contacts')
    async def _v1_parks_contacts_put(request):
        assert request.json == stub['fleet_parks_request']
        return aiohttp.web.json_response(stub['fleet_parks_response'])

    response = await web_app_client.put(
        '/api/v1/parks/contacts',
        headers=headers,
        json=stub['service_request'],
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']
