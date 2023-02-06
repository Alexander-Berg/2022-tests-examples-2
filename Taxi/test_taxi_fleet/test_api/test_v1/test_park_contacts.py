import aiohttp.web


async def test_success(web_app_client, headers, mock_fleet_parks, load_json):
    stub = load_json('success.json')

    @mock_fleet_parks('/v1/parks/contacts/retrieve')
    async def _v1_parks_contacts_get(request):
        return aiohttp.web.json_response(stub['fleet_parks_response'])

    response = await web_app_client.post(
        '/api/v1/parks/contacts', headers=headers,
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']
